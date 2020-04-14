from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


##from django.db.models.signal import post_save

# Create your models here.
##adds additional info for each user
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about_me = models.CharField(max_length=100, default='')
    major = models.CharField(max_length=50, default='')
    classes = models.CharField(max_length=500, default='')
    image = models.ImageField(upload_to='profile_image', blank=True)
    graduation_date = models.CharField(max_length=50, default='')
    experience = models.CharField(max_length=50, default='')
    contact = models.CharField(max_length=50, default='')

def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile= UserProfile.objects.create(user=kwargs['instance'])

post_save.connect(create_profile, sender= User)
