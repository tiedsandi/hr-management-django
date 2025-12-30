"""
Simplified Login Tests - Without Factory Pattern

This is a basic approach to testing that doesn't use:
- Factory-boy for data generation
- Centralized fixtures in conftest.py
- Reusable test data patterns

Compare with: tests/api/v1/accounts/test_login.py
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.mark.django_db
class TestLoginSimple:
    """Basic login tests without factory pattern"""
    
    def test_login_success(self):
        """Test successful login with valid credentials"""
        # Setup - Create user manually
        client = APIClient()
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            employee_id='EMP001',
            phone='081234567890'
        )
        
        # Execute - Login
        url = reverse('api:v1:accounts:login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = client.post(url, data, format='json')
        
        # Assert - Check response
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert 'user' in response.data
        assert response.data['user']['username'] == 'testuser'
    
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        # Setup - Create user manually
        client = APIClient()
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            employee_id='EMP001',
            phone='081234567890'
        )
        
        # Execute - Try login with wrong password
        url = reverse('api:v1:accounts:login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = client.post(url, data, format='json')
        
        # Assert - Should fail
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_inactive_user(self):
        """Test login with inactive user"""
        # Setup - Create inactive user
        client = APIClient()
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            employee_id='EMP001',
            phone='081234567890',
            is_active=False  # Inactive user
        )
        
        # Execute - Try login
        url = reverse('api:v1:accounts:login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = client.post(url, data, format='json')
        
        # Assert - Should fail
        assert response.status_code == status.HTTP_400_BAD_REQUEST


"""
COMPARISON NOTES:

1. Code Duplication:
   - Notice how we create user in EVERY test method
   - Same fields repeated multiple times
   - Factory approach: UserFactory() - one line!

2. Maintenance:
   - If User model changes (add required field), need to update ALL tests
   - Factory approach: update factory once

3. Readability:
   - Test logic mixed with data creation (7-8 lines setup)
   - Factory approach: clear separation, 1-2 lines setup

4. Reusability:
   - Can't easily reuse this user in other test files
   - Factory approach: import UserFactory anywhere

5. Flexibility:
   - Hard to create variations (admin user, user with division)
   - Factory approach: UserFactory(is_staff=True), UserFactory.create_batch(5)

LINES OF CODE:
- This simplified approach: ~85 lines for 3 tests
- Comprehensive approach: ~45 lines for 8 tests (with factory)

DEVELOPER TIME:
- Write these tests: 15 minutes
- Write with factory: 10 minutes (after factory setup)
- But: Setup factory = 20 minutes one time
- ROI: After 5 test files, factory saves time
"""
