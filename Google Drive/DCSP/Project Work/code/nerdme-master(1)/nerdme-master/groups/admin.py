from django.contrib import admin
from .models import UserProfile  ##cant import from groups folder

# Register your models here.
admin.site.register(UserProfile)