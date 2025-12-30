"""
URL Configuration for API v2/accounts
"""
from rest_framework.routers import DefaultRouter

from .viewsets import UserViewSetV2

router = DefaultRouter()
router.register(r'users', UserViewSetV2, basename='user-v2')

urlpatterns = router.urls
