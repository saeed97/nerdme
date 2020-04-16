

# account/email/confirm/asdfads/ -> activation view
from django.conf.urls import url


from .views import (
        profile, 
        UserDetailUpdateView
        
        )

urlpatterns = [
    url(r'^$', profile, name='home'),
    url(r'^update/', UserDetailUpdateView.as_view(), name='update'),

   
]

# account/email/confirm/asdfads/ -> activation view