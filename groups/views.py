from .forms import LoginForm, RegisterForm, EditProfileForm
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User

from django.utils.html import escape

from django.contrib import messages

from django.http import HttpResponse


def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'contact.html')


def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)

        return redirect('profile')

    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST or None)
        if form.is_valid():
            user = form.save()
            password = form.cleaned_data.get('password')
            form.save()
            user.set_password(password)
            # user.is_staff = user.is_superuser = True
            user.save()
            new_user = authenticate(username=user.username, password=password)
            login(request, new_user)
            return redirect('index')
        else:
            form = RegisterForm()

            args = {'form': form}
            return render(request, 'register.html', args)

    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def profile(request):
    args = {'user': request.user}
    return render(request, 'profile.html', args)


def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('profile')

    else:  ##get
        form = EditProfileForm(instance=request.user)
        args = {'form': form}
        return render(request, 'edit_profile.html', args)


def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect("profile")

        #else:
         #   return redirect("profile/password")

    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
        return render(request, 'change_password.html', args)


def groups(request):
    pass


def request(request):
    pass
