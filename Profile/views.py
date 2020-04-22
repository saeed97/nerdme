
from django.shortcuts import render,redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils.html import escape
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from .form import UserDetailChangeForm
from django.contrib import messages
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Profile


@login_required 
def profile(request):
    queryset = Profile.objects.all()
    if request.user.is_authenticated:
        if (request.user.email):
            username = request.user.email
    for user in queryset:
        if username == user.email:
            info = user

    # queryset = Profile.objects.all()
    context = {
        'user': info
    }
    return render(request, "home.html", context)



class UserDetailUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserDetailChangeForm
    template_name = 'update.html'
    

    def get_object(self):
        return self.request.user

    def get_context_data(self, *args, **kwargs):
        context = super(UserDetailUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Change Your Profile Details'
        return context

    def get_success_url(self):
        return reverse("Profile:home")


# def UserDetailUpdateView(request):
#     if request.method == 'POST':
#         form = UserDetailChangeForm(request.POST, instance=request.user)

#         if form.is_valid():
#             form.save()
#             return redirect(reverse('Profile:update'))
#     else:
#         form = UserDetailChangeForm(instance=request.user)
#         args = {'form': form}
#         return render(request, 'update.html', args)
# class UpdateProfile(UpdateView):
#     model = User
#     fields = ['first_name', 'last_name']

#     template_name = 'accounts/update.html'

#     def get_object(self):
#         return self.request.u