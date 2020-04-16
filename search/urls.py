from django.urls import url

from .views import (
        SearchProductView
        )

urlpatterns = [
    url(r'^$', SearchProductView.as_view(), name='query'),
]

