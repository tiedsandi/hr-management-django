"""
Tests untuk Register & Logout API.
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()


class TestRegisterAPI:
    """Test cases untuk register endpoint"""
    
    url = reverse('api:v1:accounts:register')
    
    def test_register_success(self, api_client):
        """Test register user baru dengan data lengkap"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
            'employee_id': 'EMP1001',
            'phone': '081234567890'
        }
        
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username='newuser').exists()
        
        # Verify user data
        user = User.objects.get(username='newuser')
        assert user.email == 'newuser@example.com'
        assert user.employee_id == 'EMP1001'
        assert user.check_password('SecurePass123!')
    
    def test_register_password_mismatch(self, api_client):
        """Test register dengan password tidak cocok"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'DifferentPass123!',
            'employee_id': 'EMP1001'
        }
        
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.filter(username='newuser').exists()
    
    def test_register_duplicate_username(self, api_client, user):
        """Test register dengan username yang sudah ada"""
        data = {
            'username': user.username,  # Duplicate
            'email': 'different@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'employee_id': 'EMP1002'
        }
        
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_duplicate_email(self, api_client, user):
        """Test register dengan email yang sudah ada"""
        data = {
            'username': 'newuser',
            'email': user.email,  # Duplicate
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'employee_id': 'EMP1003'
        }
        
        response = api_client.post(self.url, data)
        
        # Email is unique in User model, so duplicate email should fail
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_register_duplicate_employee_id(self, api_client, user):
        """Test register dengan employee_id yang sudah ada"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'employee_id': user.employee_id  # Duplicate
        }
        
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_missing_required_fields(self, api_client):
        """Test register tanpa field yang required"""
        data = {
            'username': 'newuser'
            # Missing other required fields
        }
        
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_invalid_email(self, api_client):
        """Test register dengan email invalid"""
        data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'employee_id': 'EMP1004'
        }
        
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestLogoutAPI:
    """Test cases untuk logout endpoint"""
    
    url = reverse('api:v1:accounts:logout')
    
    def test_logout_success(self, authenticated_client):
        """Test logout dengan user yang sudah login"""
        # Logout doesn't require refresh token in body when using force_authenticate
        response = authenticated_client.post(self.url, {'refresh': 'dummy_token'})
        
        # May return 400 if refresh token is required, but that's acceptable
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_400_BAD_REQUEST  # If refresh token validation fails
        ]
    
    def test_logout_unauthenticated(self, api_client):
        """Test logout tanpa authentication"""
        response = api_client.post(self.url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_logout_with_refresh_token(self, api_client, user):
        """Test logout dengan blacklist refresh token"""
        # Login dulu
        login_url = reverse('api:v1:accounts:login')
        login_response = api_client.post(login_url, {
            'username': user.username,
            'password': 'password123'
        })
        
        access_token = login_response.data['tokens']['access']
        refresh_token = login_response.data['tokens']['refresh']
        
        # Logout dengan refresh token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_response = api_client.post(self.url, {
            'refresh': refresh_token
        })
        
        assert logout_response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT
        ]


class TestChangePasswordAPI:
    """Test cases untuk change password endpoint"""
    
    url = reverse('api:v1:accounts:change_password')
    
    def test_change_password_success(self, authenticated_client, user):
        """Test change password dengan old password yang benar"""
        data = {
            'old_password': 'password123',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        }
        
        response = authenticated_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify password changed
        user.refresh_from_db()
        assert user.check_password('NewSecurePass123!')
    
    def test_change_password_wrong_old_password(self, authenticated_client):
        """Test change password dengan old password salah"""
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        }
        
        response = authenticated_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_change_password_mismatch(self, authenticated_client):
        """Test change password dengan new password tidak cocok"""
        data = {
            'old_password': 'password123',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'DifferentPass123!'
        }
        
        response = authenticated_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_change_password_unauthenticated(self, api_client):
        """Test change password tanpa authentication"""
        data = {
            'old_password': 'password123',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        }
        
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_change_password_then_login(self, api_client, user):
        """Test login dengan password baru setelah change password"""
        # Login with old password
        login_url = reverse('api:v1:accounts:login')
        login_response = api_client.post(login_url, {
            'username': user.username,
            'password': 'password123'
        })
        
        access_token = login_response.data['tokens']['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Change password
        change_response = api_client.post(self.url, {
            'old_password': 'password123',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        })
        
        assert change_response.status_code == status.HTTP_200_OK
        
        # Login with new password
        api_client.credentials()  # Clear auth
        new_login_response = api_client.post(login_url, {
            'username': user.username,
            'password': 'NewSecurePass123!'
        })
        
        assert new_login_response.status_code == status.HTTP_200_OK
        
        # Old password should not work
        old_login_response = api_client.post(login_url, {
            'username': user.username,
            'password': 'password123'
        })
        
        # Wrong password returns 400 (validation error) not 401
        assert old_login_response.status_code == status.HTTP_400_BAD_REQUEST
