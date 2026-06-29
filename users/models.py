from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True)
    def __str__(self):
        return self.username

# Removed UserProfile model in favor of fields on CustomUser