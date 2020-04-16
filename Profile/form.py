from django import forms
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.urls import reverse
from .models import Profile


class UserDetailChangeForm(forms.ModelForm):
    full_name = forms.CharField( required=False, widget=forms.TextInput(attrs={"class": 'form-control'}))

    class Meta:
        model = Profile
        fields = ['major',
                   'aboutme',
                   'location',
                   'image']