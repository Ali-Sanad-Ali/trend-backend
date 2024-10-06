

import random
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager
from django.core.mail import send_mail


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=35, unique=True)
    phone_number = models.CharField(max_length=13, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    #Configure the avatar field to store user uploads in a cloud storage service like S3 or Cloudinary for efficient and scalable media management in production environments.
    avatar = models.ImageField(upload_to='images/', default='images/avatar.jpeg', blank=True, null=True)
    
    # Currently, the OTP is only being used for password reset purposes.
    # It is generated and sent to the user's email when they request a password reset.
    # In the future, this OTP mechanism could be extended for other sensitive operations.
    last_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    created_data = models.DateTimeField(auto_now_add=True)
    updated_data = models.DateTimeField(auto_now=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
  
    def save(self, *args, **kwargs):
        '''
        Save Method      
        The save method is overridden to incorporate password hashing using Django's make_password function. This is implemented to ensure hashing even in scenarios where it could otherwise fail.
        '''
        if self.password and not self.password.startswith('pbkdf2_sha256'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    # reset password methods
    def generate_otp(self):
        self.last_otp = f'{random.randint(100000, 999999):06}'
        self.otp_expiry = timezone.now() + timedelta(minutes=10)
        self.save()

    def send_password_reset_email(self):

        mail_subject = 'Reset your password'
        # create the message as a string
        message = f"""
        Hi {self.email},

        We received a request to reset your password. Your OTP code is:

        {self.last_otp}

        This code is valid for 10 minutes. If you didn't request a password reset, you can ignore this email.

        Thanks,
        Your team
        """
        send_mail(mail_subject, message, 'admin@mywebsite.com', [self.email])


class Block(models.Model):
    """
    Block Model

    Represents a blocking relationship between two users.
    """
    blocker = models.ForeignKey(CustomUser, related_name='blocking', on_delete=models.CASCADE)
    blocked = models.ForeignKey(CustomUser, related_name='blocked_by', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')  # ensures that a user cannot block the same user more than once
        indexes = [
            models.Index(fields=['blocker']),
            models.Index(fields=['blocked']),
        ]

    def save(self, *args, **kwargs):
        from profile_app.models import Follow
        # Handle unfollow on block
        Follow.objects.filter(follower=self.blocker, following=self.blocked).delete()
        Follow.objects.filter(follower=self.blocked, following=self.blocker).delete()
        super().save(*args, **kwargs)
