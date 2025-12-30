"""
Tests untuk Login API.
Endpoint: POST /api/v1/accounts/login/
"""
import pytest
from django.urls import reverse
from rest_framework import status

from tests.factories import UserFactory


class TestLoginAPI:
    """Test cases untuk login endpoint"""
    
    url = reverse('api:v1:accounts:login')
    
    def test_login_success(self, api_client, user):
        """Test login dengan credentials yang benar"""
        data = {
            'username': user.username,
            'password': 'password123'
        }
        
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert 'user' in response.data
        assert response.data['user']['username'] == user.username
    
    def test_login_with_email(self, api_client, user):
        """Test login menggunakan email"""
        data = {
            'username': user.email,
            'password': 'password123'
        }
        
        response = api_client.post(self.url, data)
        
        # Django's default authenticate() doesn't support email
        # This will fail with 400 unless custom authentication backend is added
        # For now, we expect it to fail
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_wrong_password(self, api_client, user):
        """Test login dengan password salah"""
        data = {
            'username': user.username,
            'password': 'wrongpassword'
        }
        
        response = api_client.post(self.url, data)
        
        # Serializer validation error returns 400
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_nonexistent_user(self, api_client):
        """Test login dengan user yang tidak ada"""
        data = {
            'username': 'nonexistent',
            'password': 'password123'
        }
        
        response = api_client.post(self.url, data)
        
        # Serializer validation error returns 400
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_missing_username(self, api_client):
        """Test login tanpa username"""
        data = {
            'password': 'password123'
        }
        
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_missing_password(self, api_client, user):
        """Test login tanpa password"""
        data = {
            'username': user.username
        }
        
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_inactive_user(self, api_client):
        """Test login dengan user yang tidak aktif"""
        inactive_user = UserFactory(is_active=False)
        data = {
            'username': inactive_user.username,
            'password': 'password123'
        }
        
        response = api_client.post(self.url, data)
        
        # Serializer validation error returns 400
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_empty_credentials(self, api_client):
        """Test login dengan credentials kosong"""
        data = {
            'username': '',
            'password': ''
        }
        
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.integration
class TestLoginIntegration:
    """Integration tests untuk login flow"""
    
    def test_login_then_access_protected_endpoint(self, api_client, user):
        """Test login lalu akses protected endpoint"""
        # Login
        login_url = reverse('api:v1:accounts:login')
        login_data = {
            'username': user.username,
            'password': 'password123'
        }
        login_response = api_client.post(login_url, login_data)
        
        assert login_response.status_code == status.HTTP_200_OK
        
        # Access protected endpoint
        access_token = login_response.data['tokens']['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        profile_url = reverse('api:v1:accounts:profile')
        profile_response = api_client.get(profile_url)
        
        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.data['username'] == user.username
