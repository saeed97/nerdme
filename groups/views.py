# from groups.models import RegistrationData
from .forms import LoginForm, RegisterForm, EditProfileForm
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User

from django.utils.html import escape

from django.contrib import messages

from django.http import HttpResponse


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'contact.html')


def user_login(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login_view(request, user)

        return redirect('profile')
    else:
        return render(request, 'profiles/profile_page.html')


# def login(request):
#  context = {"form": LoginForm}
#  return render(request, "login_register/login.html", context)


def register(request):
    context = {"form": RegisterForm}
    return render(request, "login_register/register.html", context)


def addUser(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST or None)
        if form.is_valid():

            print('valid')
            form.save()

            return redirect('home')
        else:
            print('not valid')
            print(form.errors)
            form = RegisterForm()

            args = {'form': form}
            return render(request, 'login_register/register.html', args)


def logout_view(request):
    logout(request)
    return redirect('login')


def profile(request):
    args = {'form': request.user}
    return render(request, 'profile_page/profiles/profile_page.html', args)


def view_edit_profile(request):
    context = {"form": EditProfileForm}
    return render(request, "profile_page/profiles/edit_profile.html", context)

@csrf_protect
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST or None)
        if form.is_valid():

            print('valid')
            form.save()

            return redirect('profile')
        else:
            print('not valid')
            print(form.errors)
            form = EditProfileForm()

            args = {'form': form}
            return render(request, 'profile_page/profiles/edit_profile.html', args)

    else:
        print('none')
