"""
Simplified Profile Tests - Without Factory Pattern

Compare with: tests/api/v1/accounts/test_profile.py
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.mark.django_db
class TestProfileSimple:
    """Basic profile tests without factory pattern"""
    
    def test_get_profile_authenticated(self):
        """Test getting profile when authenticated"""
        # Setup - Create user and authenticate
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
        # Force authentication (bypass login)
        client.force_authenticate(user=user)
        
        # Execute - Get profile
        url = reverse('api:v1:accounts:profile')
        response = client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'
        assert response.data['email'] == 'test@example.com'
        assert response.data['first_name'] == 'Test'
        assert 'password' not in response.data  # Password should not be exposed
    
    def test_get_profile_unauthenticated(self):
        """Test getting profile when not authenticated"""
        # Setup
        client = APIClient()
        
        # Execute - Try to get profile without auth
        url = reverse('api:v1:accounts:profile')
        response = client.get(url)
        
        # Assert - Should be denied
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_profile_partial(self):
        """Test partial profile update (PATCH)"""
        # Setup - Create user and authenticate
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
        client.force_authenticate(user=user)
        
        # Execute - Update only first_name
        url = reverse('api:v1:accounts:profile')
        data = {'first_name': 'Updated'}
        response = client.patch(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'User'  # Should remain unchanged
        
        # Verify database updated
        user.refresh_from_db()
        assert user.first_name == 'Updated'
    
    def test_cannot_update_username(self):
        """Test that username cannot be changed"""
        # Setup - Create user and authenticate
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
        client.force_authenticate(user=user)
        
        # Execute - Try to update username
        url = reverse('api:v1:accounts:profile')
        data = {'username': 'newusername'}
        response = client.patch(url, data, format='json')
        
        # Assert - Request succeeds but username unchanged
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'  # Still original
        
        # Verify database NOT updated
        user.refresh_from_db()
        assert user.username == 'testuser'


"""
COMPARISON WITH COMPREHENSIVE APPROACH:

1. Setup Repetition:
   Simplified:
   - 9 lines of user creation in EACH test
   - Total: 36 lines of repeated setup code
   
   Comprehensive:
   - UserFactory() = 1 line
   - authenticated_client fixture = 0 lines (automatic)
   - Total: ~4 lines for all tests

2. Authentication Handling:
   Simplified:
   - client = APIClient() every time
   - client.force_authenticate(user=user) every time
   
   Comprehensive:
   - @pytest.fixture authenticated_client - done once
   - All tests just use 'authenticated_client' parameter

3. Test Variations:
   Simplified:
   - Want to test admin user? Copy-paste and modify
   - Want to test user with division? More copy-paste
   
   Comprehensive:
   - admin_user fixture already exists
   - user_with_division fixture already exists
   - Just use the fixture you need

4. Database State:
   Simplified:
   - Manual cleanup needed (pytest-django handles it but...)
   - Each test creates from scratch
   
   Comprehensive:
   - Factory handles transient vs persisted
   - Can use .build() for non-DB objects

REAL WORLD SCENARIO:

Imagine you need to test 10 different endpoints, each needing:
- Regular user tests (5 tests each) = 50 tests
- Admin user tests (3 tests each) = 30 tests  
- User with division tests (2 tests each) = 20 tests
Total: 100 tests

Simplified Approach:
- Lines of setup code: 100 tests × 9 lines = 900 lines
- Time to write: 100 tests × 2 min = 200 minutes (~3.3 hours)
- Time to modify if User model changes: Update 100 places = 50 minutes

Comprehensive Approach:
- Lines of setup code: 3 fixtures + 2 factories = ~50 lines
- Time to write: 100 tests × 1 min = 100 minutes (~1.7 hours)
- Initial setup time: 30 minutes
- Total: 2.2 hours vs 3.3 hours (save 1 hour)
- Time to modify if User model changes: Update 1 factory = 2 minutes

ROI CALCULATION:
- Investment: 30 minutes factory setup
- Savings: 1 hour on initial write + 48 minutes on future changes
- Break-even: After ~30 tests
- This project: 41 tests now, will have 200+ tests eventually
- Total savings: 5-10 hours over project lifetime
"""
