from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('login/', views.login_view, name="login"),

    path('register/', views.register, name="register"),

    path('logout/', views.logout_view, name="logout"),

    path('contact/', views.about, name="contact"),

    path('profile/', views.profile, name="profile"),

    path('groups/', views.groups, name="groups"),

    path('request/', views.request, name="request"),

    path('profile/edit/', views.edit_profile, name="edit_profile"),

    path('profile/password/', views.change_password, name="change_password"),

]
