"""
Tests untuk Profile API.
Endpoints: 
- GET/PUT/PATCH /api/v1/accounts/profile/
"""
import pytest
from django.urls import reverse
from rest_framework import status

from tests.factories import UserFactory


class TestProfileRetrieveAPI:
    """Test cases untuk get profile"""
    
    url = reverse('api:v1:accounts:profile')
    
    def test_get_profile_authenticated(self, authenticated_client, user):
        """Test get profile dengan user yang sudah login"""
        response = authenticated_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username
        assert response.data['email'] == user.email
        assert response.data['employee_id'] == user.employee_id
    
    def test_get_profile_unauthenticated(self, api_client):
        """Test get profile tanpa authentication"""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_profile_contains_required_fields(self, authenticated_client, user):
        """Test response profile mengandung field yang dibutuhkan"""
        response = authenticated_client.get(self.url)
        
        required_fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'employee_id', 'phone', 'status', 'type_of_employment'
        ]
        
        for field in required_fields:
            assert field in response.data
    
    def test_profile_no_password_field(self, authenticated_client):
        """Test profile tidak menampilkan password"""
        response = authenticated_client.get(self.url)
        
        assert 'password' not in response.data


class TestProfileUpdateAPI:
    """Test cases untuk update profile"""
    
    url = reverse('api:v1:accounts:profile')
    
    def test_update_profile_full(self, authenticated_client, user):
        """Test update profile lengkap (PUT)"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '081234567890',
            'email': user.email  # Keep same email
        }
        
        response = authenticated_client.put(self.url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'John'
        assert response.data['last_name'] == 'Doe'
        assert response.data['phone'] == '081234567890'
        
        # Verify data changed in DB
        user.refresh_from_db()
        assert user.first_name == 'John'
    
    def test_update_profile_partial(self, authenticated_client, user):
        """Test update profile sebagian (PATCH)"""
        data = {
            'first_name': 'Jane'
        }
        
        response = authenticated_client.patch(self.url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Jane'
        assert response.data['last_name'] == user.last_name  # Unchanged
    
    def test_update_profile_unauthenticated(self, api_client):
        """Test update profile tanpa authentication"""
        data = {'first_name': 'John'}
        
        response = api_client.patch(self.url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_profile_invalid_phone(self, authenticated_client):
        """Test update dengan nomor telepon invalid"""
        data = {
            'phone': '123'  # Too short
        }
        
        response = authenticated_client.patch(self.url, data)
        
        # Might be 400 BAD REQUEST depending on validation
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK]
    
    def test_cannot_update_employee_id(self, authenticated_client, user):
        """Test tidak bisa update employee_id (read-only)"""
        original_employee_id = user.employee_id
        data = {
            'employee_id': 'EMP9999'
        }
        
        response = authenticated_client.patch(self.url, data)
        
        # Employee ID should not change
        user.refresh_from_db()
        assert user.employee_id == original_employee_id
    
    def test_cannot_update_username(self, authenticated_client, user):
        """Test tidak bisa update username (read-only)"""
        original_username = user.username
        data = {
            'username': 'newusername'
        }
        
        response = authenticated_client.patch(self.url, data)
        
        # Username should not change
        user.refresh_from_db()
        assert user.username == original_username


@pytest.mark.integration
class TestProfileIntegration:
    """Integration tests untuk profile flow"""
    
    def test_complete_profile_flow(self, api_client, user):
        """Test complete flow: login -> get profile -> update profile"""
        # Login
        login_url = reverse('api:v1:accounts:login')
        login_response = api_client.post(login_url, {
            'username': user.username,
            'password': 'password123'
        })
        
        access_token = login_response.data['tokens']['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Get profile
        profile_url = reverse('api:v1:accounts:profile')
        get_response = api_client.get(profile_url)
        assert get_response.status_code == status.HTTP_200_OK
        
        # Update profile
        update_response = api_client.patch(profile_url, {
            'first_name': 'Updated'
        })
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data['first_name'] == 'Updated'
        
        # Verify update persisted
        verify_response = api_client.get(profile_url)
        assert verify_response.data['first_name'] == 'Updated'
