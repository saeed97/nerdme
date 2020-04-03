#!/home/stepsizestrategies/.local/bin/python3
# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth import authenticate, models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label='Username')
    password = forms.CharField(max_length=100, label='Password', widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("invalid entrance!")
        return super(LoginForm, self).clean()


class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=100, label='username')
    password = forms.CharField(max_length=100, label='password', widget=forms.PasswordInput)
    description = forms.CharField(max_length=100, label='description')
    status = forms.CharField(max_length=100, label='description')

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'description',
            'status',


        ]


class EditProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = {
            'first_name',
            'last_name',
            'email',
        }
        ##exclude = {}  gets rid of unwanted fields
