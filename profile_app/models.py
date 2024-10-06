import os
from django.db import models
from authentication.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.storage import default_storage


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile',null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    background_pic = models.ImageField(upload_to='background_pics', blank=True, null=True)
    hide_avatar = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.avatar and self.user and self.user.avatar.name != 'images/avatar.jpeg':
            
            self.avatar = self.user.avatar
        super().save(*args, **kwargs)

    def post_count(self):
        return self.posts.count()

    def __str__(self):
        return self.user.username

    def follow_count(self):
        return self.user.following.count()
    
    def follower_count(self):
        return self.user.followers.count()
    
    def vlog_count(self):
        return self.user.video_set.count()


class Follow(models.Model):
    follower = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE,null=True)
    following = models.ForeignKey(CustomUser, related_name='followers', on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'
    
    def clean(self):
        # Check if a follow instance already exists with the same follower and following
        if Follow.objects.filter(following=self.following, follower=self.follower).exists():
            raise ValidationError('You are already following this user.')




@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        if instance.avatar.name != 'images/avatar.jpeg':  # Check if a custom avatar is provided
            profile.avatar = instance.avatar
            profile.save()



@receiver(post_save, sender=Profile)
def update_user_from_profile(sender, instance, created, **kwargs):
  
    if created:
        return  # Nothing to update if it's a new profile

    if instance.user and instance.user.avatar != instance.avatar:
        instance.user.avatar = instance.avatar
        instance.user.save()