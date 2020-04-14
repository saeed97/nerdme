#!/home/stepsizestrategies/.local/bin/python3
# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth import authenticate, models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UserProfile


class RegisterForm(UserCreationForm):
    username = forms.CharField(max_length=100, required=True,
                               widget=forms.TextInput(attrs={'class': 'form_control', 'name': 'username',
                                                             'id': 'name', "placeholder": 'Your Name'}))
    email = forms.EmailField(max_length=100, required=True,
                             widget=forms.EmailInput(attrs={'class': 'form_control', 'name': 'email',
                                                            'id': 'email', "placeholder": 'Your Email'}))
    password1 = forms.CharField(max_length=100, required=True,
                                widget=forms.PasswordInput(attrs={'class': 'form_control', 'name': 'password',
                                                                  'id': 'pass', "placeholder": 'Your Password'}))
    password2 = forms.CharField(max_length=100, required=True,
                                widget=forms.PasswordInput(attrs={'class': 'form_control', 'name': 'password',
                                                                  'id': 'pass', "placeholder": 'Repeat Your Password'}))



    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',
        )


    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        #user.username = self.cleaned_data
        user.email = self.cleaned_data['email']
        #user.password1 = self.cleaned_data

        if commit:
            user.save()

        return user


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True,
                               widget=forms.TextInput(attrs={'class': 'form_control', 'name': 'username',
                                                             'id': 'name', "placeholder": 'Your Name'}))
    password1 = forms.CharField(max_length=100, required=True,
                               widget=forms.PasswordInput(attrs={'class': 'form_control', 'name': 'password',
                                                                 'id': 'pass', "placeholder": 'Your Password'}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password1 = self.cleaned_data.get('password')
        if username and password1:
            user = authenticate(username=username, password=password1)
            if not user:
                raise forms.ValidationError("invalid entrance!")
        return super(LoginForm, self).clean()


class EditProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = {
            'classes',
            'major',
            'about_me',
            'contact',
            'graduation_date',
        }
        ##exclude = {}  gets rid of unwanted fields
        ## include classes

    def save(self, commit=True):
        user = super(EditProfileForm, self).save(commit=False)
        user.classes = self.cleaned_data['classes']
        user.major = self.cleaned_data['major']
        user.about_me = self.cleaned_data['about_me']
        user.contact = self.cleaned_data['contact']
        user.graduation_date = self.cleaned_data['graduation_date']

        if commit:
            user.save()

        return user
