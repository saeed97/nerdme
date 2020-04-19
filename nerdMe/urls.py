"""nerdMe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView, RedirectView


# from accounts.views import LoginView, RegisterView, GuestRegisterView
from accounts.views import LoginView, RegisterView




from .views import home_page, contact_page

urlpatterns = [
    url(r'^$', home_page, name='home'),
    #url(r'^about/$', about_page, name='about'),
    #url(r'^accounts/$', RedirectView.as_view(url='/account')),
    url(r'^account/', include(("accounts.urls",'account'), namespace='account')),

    url(r'^accounts/', include("accounts.passwords.urls")),
    url(r'^contact/$', contact_page, name='contact'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    # url(r'^register/guest/$', GuestRegisterView.as_view(), name='guest_register'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^profile/', include(("Profile.urls",'Profile'), namespace='Profile')),
    url(r'^groups/', include(('groups.urls','groups'), namespace="groups")),
    url(r'^bootstrap/$', TemplateView.as_view(template_name='bootstrap/example.html')),
   # url(r'^search/', include("search.urls", namespace='search')),
    url(r'^settings/$', RedirectView.as_view(url='/account')),
    url(r'^admin/', admin.site.urls),
]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
