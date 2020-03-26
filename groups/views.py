from groups.forms import LoginForm, RegisterForm
from django.shortcuts import render,redirect

from django.contrib.auth import authenticate, login, logout

from django.utils.html import escape

from django.contrib import messages

from django.http import HttpResponse


def index(request):
    return  render(request, 'index.html')


def about(request):

    return  render(request, 'contact.html')
def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)

        return redirect('index')

    return render(request, 'login.html')


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        password = form.cleaned_data.get('password')
        user.set_password(password)
        # user.is_staff = user.is_superuser = True
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        return redirect('index')

    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('login')