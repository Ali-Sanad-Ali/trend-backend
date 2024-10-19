import os

from django.core.files.base import File

from celery import shared_task
from io import BytesIO
from PIL import Image
from moviepy.editor import VideoFileClip

from vlog.models import Video

@shared_task()
def create_video_thumbnail(video_pk):
    video_obj = Video.objects.get(pk=video_pk)
    video_path = video_obj.video.path

    # Extract a frame from the video (at 1 second, or earlier if the video is shorter)
    with VideoFileClip(video_path) as video:
        duration = video.duration
        thumbnail_time = min(1, duration)  # Take the frame at 1 second or earlier
        frame = video.get_frame(thumbnail_time)  # Get a frame (numpy array)
        
        # Convert the numpy array to an image and save it
        image = Image.fromarray(frame)
        new_width, new_height = (160, 160)
        image.thumbnail((new_width, new_height))
        
        img_temp = BytesIO()
        image.save(img_temp, "PNG")

        # Save the thumbnail as a file in the thumbnail field
        video_obj.thumbnail = File(img_temp, os.path.basename(video_obj.video.name).split(".")[0] + ".png")
        video_obj.save()