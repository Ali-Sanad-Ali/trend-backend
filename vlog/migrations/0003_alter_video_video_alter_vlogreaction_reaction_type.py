# Generated by Django 4.2.16 on 2024-10-18 20:01

import django.core.validators
from django.db import migrations, models
import vlog.models


class Migration(migrations.Migration):

    dependencies = [
        ('vlog', '0002_vlogreaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='video',
            field=models.FileField(upload_to='vlogs/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'mkv', 'webm', '3gp']), vlog.models.validate_video_size, vlog.models.validate_video_duration]),
        ),
        migrations.AlterField(
            model_name='vlogreaction',
            name='reaction_type',
            field=models.CharField(choices=[('love', '❤️ Love'), ('like', '👍 Like'), ('haha', '😂 Haha'), ('wow', '😮 Wow'), ('crying', '😭 crying'), ('disgusting', '🤮 disgusting')], max_length=20),
        ),
    ]
