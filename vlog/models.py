import os
import tempfile

from django.conf import settings
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.core.files.uploadedfile import InMemoryUploadedFile

from moviepy.editor import VideoFileClip
import logging
import requests

from authentication.models import CustomUser  # Assuming this is your user model

# Constants
MAX_VIDEO_SIZE = settings.MAX_VIDEO_SIZE
MAX_VIDEO_DURATION = settings.MAX_VIDEO_DURATION

# Logger setup
logger = logging.getLogger(__name__)

def validate_video_size(file):
    if file.size > MAX_VIDEO_SIZE:
        raise ValidationError(f"Video file size should not exceed {MAX_VIDEO_SIZE / (1024 * 1024)} MB.")

def validate_video_duration(file):
    if isinstance(file, InMemoryUploadedFile):
        # Create a temporary file for in-memory uploaded files
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
            temp_video_path = temp_file.name
    else:
        # Use file.path for files stored in file-based backends
        temp_video_path = file.path

    # Now you can use the temp_video_path with VideoFileClip
    try:
        with VideoFileClip(temp_video_path) as video:
            duration = video.duration
            if duration > MAX_VIDEO_DURATION:  # Define your MAX_DURATION
                raise ValidationError(f"Video duration exceeds the maximum limit of {MAX_VIDEO_DURATION} seconds.")
    finally:
        # Clean up the temporary file for in-memory uploads
        if isinstance(file, InMemoryUploadedFile):
            os.remove(temp_video_path)

class Video(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    # Configure the video field to store user uploads in a cloud storage service like S3 or Cloudinary for efficient and scalable media management in production environments.
    video = models.FileField(
        upload_to='vlogs/',
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'mkv', 'webm', '3gp']),
            validate_video_size
        ]
    )
    duration = models.DurationField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        created = self.pk is None
        with transaction.atomic():
            super().save(*args, **kwargs)

            try:
                # Download the video temporarily for processing
                with tempfile.NamedTemporaryFile(delete=True, suffix='.mp4') as temp_file:
                    response = requests.get(self.video.url, stream=True)
                    if response.status_code == 200:
                        for chunk in response.iter_content(chunk_size=8192):
                            temp_file.write(chunk)
                        temp_file.flush()

                        # Open and validate the video duration
                        with VideoFileClip(temp_file.name) as video:
                            duration = video.duration
                            if duration > MAX_VIDEO_DURATION:
                                raise ValidationError(f"Video duration exceeds the maximum limit of {MAX_VIDEO_DURATION} seconds.")
            except Exception as e:
                raise ValidationError(f"Unable to process video file: {e}")

            if created:
                from vlog.tasks import create_video_thumbnail
                transaction.on_commit(
                    lambda: create_video_thumbnail.delay(self.pk)
                )
    def __str__(self):
        return self.title

class VlogComment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='vlog_comments')
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}..."

class VlogLike(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='vlog_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('video', 'user')

    def __str__(self):
        return f"{self.user.username} liked video {self.video.id}"

class VlogReaction(models.Model):
    REACTION_CHOICES = [
        ('love', '❤️ Love'),
        ('like', '👍 Like'),
        ('haha', '😂 Haha'),
        ('wow', '😮 Wow'),
        ('crying', '😭 crying'),
        ('disgusting', '🤮 disgusting'),
        # Add more or remove reactions as needed
    ]

    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='vlog_reactions')
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('video', 'user', 'reaction_type')

    def __str__(self):
        return f"{self.user.username} reacted {self.get_reaction_type_display()} to video {self.video.id}"

    @classmethod
    def toggle_reaction(cls, video, user, reaction_type):
        """
        Toggle a reaction. If the reaction exists, remove it. Otherwise, create it.
        """
        try:
            reaction = cls.objects.get(video=video, user=user, reaction_type=reaction_type)
            reaction.delete()
            return False
        except cls.DoesNotExist:
            cls.objects.create(video=video, user=user, reaction_type=reaction_type)
            return True
