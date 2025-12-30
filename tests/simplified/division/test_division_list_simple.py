"""
Simplified Division List API Tests

Compare with: tests/api/v1/accounts/division/test_division_list.py
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Division, User


@pytest.mark.django_db
class TestDivisionListSimple:
    """Division list endpoint tests - Simplified approach"""

    def test_list_divisions_authenticated(self):
        """Test listing divisions with authentication"""
        # Setup: Create user manually
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            employee_id='EMP001',
            phone='081234567890'
        )
        
        # Setup: Create divisions manually
        Division.objects.create(
            code='HR',
            name='HR Department',
            description='Human Resources',
            level=0
        )
        Division.objects.create(
            code='IT',
            name='IT Department',
            description='Information Technology',
            level=0
        )
        
        # Setup: Authenticate client
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Make request
        url = reverse('api:v1:accounts:division-list')
        response = client.get(url)
        
        # Assert: Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert len(response.data['results']) == 2

    def test_list_divisions_unauthenticated(self):
        """Test listing divisions without authentication"""
        # Setup: Create division
        Division.objects.create(
            code='HR',
            name='HR Department',
            level=0
        )
        
        # Setup: Client without authentication
        client = APIClient()
        
        # Act: Make request
        url = reverse('api:v1:accounts:division-list')
        response = client.get(url)
        
        # Assert: Should fail
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_search_divisions(self):
        """Test searching divisions by name"""
        # Setup: Create user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            employee_id='EMP001',
            phone='081234567890'
        )
        
        # Setup: Create divisions
        Division.objects.create(code='HR', name='HR Department', level=0)
        Division.objects.create(code='IT', name='IT Department', level=0)
        Division.objects.create(code='FIN', name='Finance Department', level=0)
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Search for 'HR'
        url = reverse('api:v1:accounts:division-list')
        response = client.get(url, {'search': 'HR'})
        
        # Assert: Only HR department found
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == 'HR Department'


@pytest.mark.django_db
class TestDivisionCreateSimple:
    """Division create endpoint tests - Simplified approach"""

    def test_create_division_success(self):
        """Test creating a new division"""
        # Setup: Create and authenticate user
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            employee_id='EMP999',
            phone='081234567890'
        )
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Create division
        url = reverse('api:v1:accounts:division-list')
        data = {
            'code': 'HR',
            'name': 'HR Department',
            'description': 'Human Resources Department',
            'parent': None,
        }
        response = client.post(url, data, format='json')
        
        # Assert: Division created
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == 'HR'
        assert response.data['name'] == 'HR Department'
        assert response.data['level'] == 0
        
        # Verify in database
        assert Division.objects.filter(code='HR').exists()

    def test_create_sub_division(self):
        """Test creating a sub-division with parent"""
        # Setup: Create user
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            employee_id='EMP999',
            phone='081234567890'
        )
        
        # Setup: Create parent division
        parent = Division.objects.create(
            code='HR',
            name='HR Department',
            level=0
        )
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Create sub-division
        url = reverse('api:v1:accounts:division-list')
        data = {
            'code': 'HR-REC',
            'name': 'HR Recruitment',
            'description': 'Recruitment Team',
            'parent': parent.id,
        }
        response = client.post(url, data, format='json')
        
        # Assert: Sub-division created with correct level
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == 'HR-REC'
        assert response.data['level'] == 1  # Parent is 0, child should be 1
        
        # Verify relationship
        sub_division = Division.objects.get(code='HR-REC')
        assert sub_division.parent.id == parent.id

    def test_create_division_duplicate_code(self):
        """Test creating division with duplicate code fails"""
        # Setup: Create user
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            employee_id='EMP999',
            phone='081234567890'
        )
        
        # Setup: Create existing division
        Division.objects.create(
            code='HR',
            name='HR Department',
            level=0
        )
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Try to create duplicate
        url = reverse('api:v1:accounts:division-list')
        data = {
            'code': 'HR',  # Duplicate!
            'name': 'Another HR Department',
            'parent': None,
        }
        response = client.post(url, data, format='json')
        
        # Assert: Should fail
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'code' in response.data

    def test_create_division_unauthenticated(self):
        """Test creating division without authentication"""
        # Setup: Client without authentication
        client = APIClient()
        
        # Act: Try to create division
        url = reverse('api:v1:accounts:division-list')
        data = {
            'code': 'HR',
            'name': 'HR Department',
            'parent': None,
        }
        response = client.post(url, data, format='json')
        
        # Assert: Should fail
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDivisionTreeSimple:
    """Division tree endpoint tests - Simplified approach"""

    def test_get_division_tree(self):
        """Test getting division hierarchy tree"""
        # Setup: Create user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            employee_id='EMP001',
            phone='081234567890'
        )
        
        # Setup: Create hierarchy
        hr = Division.objects.create(code='HR', name='HR Department', level=0)
        hr_rec = Division.objects.create(
            code='HR-REC',
            name='HR Recruitment',
            parent=hr,
            level=1
        )
        hr_training = Division.objects.create(
            code='HR-TRA',
            name='HR Training',
            parent=hr,
            level=1
        )
        
        it = Division.objects.create(code='IT', name='IT Department', level=0)
        it_dev = Division.objects.create(
            code='IT-DEV',
            name='IT Development',
            parent=it,
            level=1
        )
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Get tree
        url = reverse('api:v1:accounts:division-tree')
        response = client.get(url)
        
        # Assert: Tree structure returned
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2  # 2 top-level divisions
        
        # Verify HR branch
        hr_data = next(d for d in response.data['tree'] if d['code'] == 'HR')
        assert len(hr_data['children']) == 2
        assert any(c['code'] == 'HR-REC' for c in hr_data['children'])
        
        # Verify IT branch
        it_data = next(d for d in response.data['tree'] if d['code'] == 'IT')
        assert len(it_data['children']) == 1
        assert it_data['children'][0]['code'] == 'IT-DEV'
