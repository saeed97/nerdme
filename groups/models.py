from django.db import models
from django.contrib.auth.models import User


##from django.db.models.signal import post_save

# Create your models here.
##adds additional info for each user
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    description = models.CharField(max_length=100, default='')
    major = models.CharField(max_length=50, default='')
    status = models.CharField(max_length=50, default='')
    image = models.ImageField(upload_to='profile_image', blank=True)
