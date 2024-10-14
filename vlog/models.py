import os
import tempfile
import requests
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files import File
from PIL import Image
from moviepy.editor import VideoFileClip
import logging

from authentication.models import CustomUser  # Assuming this is your user model

# Constants
MAX_VIDEO_SIZE = 200 * 1024 * 1024  # 200 MB
MAX_VIDEO_DURATION = timezone.timedelta(seconds=15)

# Logger setup
logger = logging.getLogger(__name__)

def validate_video_size(file):
    """
    Validate the size of the uploaded video file.
    Raises ValidationError if the file size exceeds MAX_VIDEO_SIZE.
    """
    if file.size > MAX_VIDEO_SIZE:
        raise ValidationError(f"File size should not exceed {MAX_VIDEO_SIZE / (1024 * 1024)} MB.")

def validate_video_duration(duration):
    """
    Validate the duration of the uploaded video.
    Raises ValidationError if the duration exceeds MAX_VIDEO_DURATION.
    """
    if duration > MAX_VIDEO_DURATION:
        raise ValidationError(f"Video duration should not exceed {MAX_VIDEO_DURATION.total_seconds()} seconds.")
def generate_thumbnail(video_path, output_path, time=0.0):
    """
    Generate a thumbnail image from a video file.

    Args:
    video_path (str): Path to the video file.
    output_path (str): Path where the thumbnail should be saved.
    time (float): Time in seconds at which to capture the thumbnail. Defaults to 0.0 (start of video).

    Returns:
    bool: True if thumbnail was generated successfully, False otherwise.
    """
    try:
        with VideoFileClip(video_path) as video:
            # Capture frame at specified time
            frame = video.get_frame(time)

            # Convert frame to PIL Image and save
            image = Image.fromarray(frame)
            image.save(output_path, format='JPEG')
        return True
    except Exception as e:
        logger.error(f"Error generating thumbnail: {str(e)}")
        return False

class Video(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    #Configure the video field to store user uploads in a cloud storage service like S3 or Cloudinary for efficient and scalable media management in production environments.
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
        """
        Custom save method to process the video file, calculate duration, and generate thumbnail.
        """
        is_new = self.pk is None

        # Process video file
        #RECOMMEDATION :Use Redis for caching and Celery for asynchronous video processing to enhance scalability and performance.
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
            # Download video file if it's stored remotely (e.g., S3)
            if 'http' in self.video.url:
                temp_video.write(requests.get(self.video.url).content)
            else:
                temp_video.write(self.video.read())
            temp_video_path = temp_video.name

        thumbnail_path = None
        try:
            with VideoFileClip(temp_video_path) as video:
                # Calculate and validate duration
                duration = timezone.timedelta(seconds=video.duration)
                validate_video_duration(duration)

                # Generate and save thumbnail IN THE FIRST SECOND OF THE VIDEO
                thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'video_thumbnails', f'{self.pk}_thumb.jpg')
                if generate_thumbnail(temp_video_path, thumbnail_path, time=1.0):
                    with open(thumbnail_path, 'rb') as thumb_file:
                        self.thumbnail.save(f'{self.pk}_thumb.jpg', File(thumb_file), save=False)

                # Set duration and save changes
                self.duration = duration
                super().save(*args, **kwargs)

        except ValidationError as ve:
            # Handle validation error gracefully
            logger.error(f"Validation error: {ve.messages[0]}")
            raise ve

        finally:
            # Clean up temporary files
            os.remove(temp_video_path)
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)

    @property
    def like_count(self):
        """
        Returns the number of likes for this video.
        """
        return self.likes.count()

    @property
    def comment_count(self):
        """
        Returns the number of comments for this video.
        """
        return self.comments.count()

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