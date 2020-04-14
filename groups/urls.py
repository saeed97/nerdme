from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('register', views.register, name="register"),

    path('logout/', views.logout_view, name="logout"),

    path('contact/', views.about, name="contact"),

    path('profile/', views.profile, name="profile"),

    path('edit_profile', views.edit_profile, name="edit_profile"),

    path('addUser', views.addUser, name="addUser"),

    path('login_register/login', LoginView.as_view(template_name='login_register/login.html'), name="login"),

    path('view_edit_profile', views.view_edit_profile, name="view_edit_profile"),



]
