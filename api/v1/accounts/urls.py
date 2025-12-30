from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api.v1.accounts.viewsets.division import DivisionViewSet
from api.v1.accounts.viewsets.user import (
    ChangePasswordView,
    LoginView,
    LogoutView,
    ProfileView,
    RegisterView,
)

app_name = 'accounts'

# Router for viewsets
router = DefaultRouter()
router.register(r'divisions', DivisionViewSet, basename='division')

urlpatterns = [
    # Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Division ViewSet
    path('', include(router.urls)),
]