"""
URL Configuration for API v2
"""
from django.urls import include, path

urlpatterns = [
    path('accounts/', include('api.v2.accounts.urls')),
]
