"""
Tests untuk Token Refresh API.
Endpoint: POST /api/v1/accounts/token/refresh/
"""
import pytest
from django.urls import reverse
from rest_framework import status


class TestTokenRefreshAPI:
    """Test cases untuk token refresh endpoint"""
    
    url = reverse('api:v1:accounts:token_refresh')
    
    def test_refresh_token_success(self, api_client, user):
        """Test refresh token dengan refresh token yang valid"""
        # Login dulu untuk dapat refresh token
        login_url = reverse('api:v1:accounts:login')
        login_data = {
            'username': user.username,
            'password': 'password123'
        }
        login_response = api_client.post(login_url, login_data)
        refresh_token = login_response.data['tokens']['refresh']
        
        # Refresh token
        data = {'refresh': refresh_token}
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert response.data['access'] != login_response.data['tokens']['access']  # New token
    
    def test_refresh_token_invalid(self, api_client):
        """Test refresh dengan token invalid"""
        data = {'refresh': 'invalid_token_here'}
        
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token_missing(self, api_client):
        """Test refresh tanpa token"""
        data = {}
        
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_refresh_token_empty(self, api_client):
        """Test refresh dengan token kosong"""
        data = {'refresh': ''}
        
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_multiple_refresh(self, api_client, user):
        """Test refresh token multiple kali"""
        # Login
        login_url = reverse('api:v1:accounts:login')
        login_data = {
            'username': user.username,
            'password': 'password123'
        }
        login_response = api_client.post(login_url, login_data)
        refresh_token = login_response.data['tokens']['refresh']
        
        # First refresh
        response1 = api_client.post(self.url, {'refresh': refresh_token})
        assert response1.status_code == status.HTTP_200_OK
        access_token_1 = response1.data['access']
        
        # Second refresh with SAME token will FAIL because ROTATE_REFRESH_TOKENS=True
        # The first refresh blacklisted the old token and returned a new one
        response2 = api_client.post(self.url, {'refresh': refresh_token})
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED  # Token blacklisted
        
        # But if we use the NEW refresh token from response1, it should work
        if 'refresh' in response1.data:
            new_refresh_token = response1.data['refresh']
            response3 = api_client.post(self.url, {'refresh': new_refresh_token})
            assert response3.status_code == status.HTTP_200_OK
            access_token_3 = response3.data['access']
            
            # Tokens should be different
            assert access_token_1 != access_token_3


@pytest.mark.integration
class TestTokenRefreshIntegration:
    """Integration tests untuk token refresh flow"""
    
    def test_use_refreshed_token(self, api_client, user):
        """Test menggunakan token yang sudah di-refresh untuk akses endpoint"""
        # Login
        login_url = reverse('api:v1:accounts:login')
        login_response = api_client.post(login_url, {
            'username': user.username,
            'password': 'password123'
        })
        
        # Refresh token
        refresh_url = reverse('api:v1:accounts:token_refresh')
        refresh_response = api_client.post(refresh_url, {
            'refresh': login_response.data['tokens']['refresh']
        })
        
        # Use new access token
        new_access_token = refresh_response.data['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        
        # Access protected endpoint
        profile_url = reverse('api:v1:accounts:profile')
        profile_response = api_client.get(profile_url)
        
        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.data['username'] == user.username
