"""
Simplified Division Detail API Tests

Compare with: tests/api/v1/accounts/division/test_division_detail.py
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Division, User


@pytest.mark.django_db
class TestDivisionDetailSimple:
    """Division detail endpoint tests - Simplified approach"""

    def test_get_division_detail(self):
        """Test getting division detail"""
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
        
        # Setup: Create division
        division = Division.objects.create(
            code='HR',
            name='HR Department',
            description='Human Resources',
            level=0
        )
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Get detail
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        response = client.get(url)
        
        # Assert: Detail returned
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == division.id
        assert response.data['code'] == 'HR'
        assert response.data['name'] == 'HR Department'
        assert response.data['description'] == 'Human Resources'

    def test_get_division_with_hierarchy(self):
        """Test getting division detail with children and ancestors"""
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
        
        # Setup: Create hierarchy (grandparent -> parent -> child)
        grandparent = Division.objects.create(
            code='HR',
            name='HR Department',
            level=0
        )
        parent = Division.objects.create(
            code='HR-MGR',
            name='HR Management',
            parent=grandparent,
            level=1
        )
        child = Division.objects.create(
            code='HR-REC',
            name='HR Recruitment',
            parent=parent,
            level=2
        )
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Get parent detail
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': parent.id})
        response = client.get(url)
        
        # Assert: Has children and ancestors
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['children']) == 1
        assert response.data['children'][0]['code'] == 'HR-REC'
        assert len(response.data['ancestors']) == 1
        assert response.data['ancestors'][0]['code'] == 'HR'


@pytest.mark.django_db
class TestDivisionUpdateSimple:
    """Division update endpoint tests - Simplified approach"""

    def test_update_division_full(self):
        """Test full update of division (PUT)"""
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
        
        # Setup: Create division
        division = Division.objects.create(
            code='HR',
            name='HR Department',
            description='Old description',
            level=0
        )
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Full update
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        data = {
            'code': 'HR',
            'name': 'Human Resources Department',
            'description': 'New updated description',
            'parent': None,
        }
        response = client.put(url, data, format='json')
        
        # Assert: Updated
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Human Resources Department'
        assert response.data['description'] == 'New updated description'
        
        # Verify in database
        division.refresh_from_db()
        assert division.name == 'Human Resources Department'

    def test_update_division_partial(self):
        """Test partial update of division (PATCH)"""
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
        
        # Setup: Create division
        division = Division.objects.create(
            code='HR',
            name='HR Department',
            description='Original description',
            level=0
        )
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Partial update (only description)
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        data = {'description': 'Partially updated description'}
        response = client.patch(url, data, format='json')
        
        # Assert: Only description changed
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 'HR'  # Unchanged
        assert response.data['name'] == 'HR Department'  # Unchanged
        assert response.data['description'] == 'Partially updated description'  # Changed

    def test_update_division_change_parent(self):
        """Test changing division parent"""
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
        
        # Setup: Create divisions
        hr = Division.objects.create(code='HR', name='HR Department', level=0)
        it = Division.objects.create(code='IT', name='IT Department', level=0)
        sub_div = Division.objects.create(
            code='REC',
            name='Recruitment',
            parent=hr,
            level=1
        )
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Change parent from HR to IT
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': sub_div.id})
        data = {
            'code': 'REC',
            'name': 'Recruitment',
            'parent': it.id,
        }
        response = client.put(url, data, format='json')
        
        # Assert: Parent changed
        assert response.status_code == status.HTTP_200_OK
        
        # Verify in database
        sub_div.refresh_from_db()
        assert sub_div.parent.id == it.id


@pytest.mark.django_db
class TestDivisionDeleteSimple:
    """Division delete endpoint tests - Simplified approach"""

    def test_delete_division_success(self):
        """Test soft deleting a division"""
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
        
        # Setup: Create division
        division = Division.objects.create(
            code='HR',
            name='HR Department',
            level=0
        )
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Delete division
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        response = client.delete(url)
        
        # Assert: Soft deleted
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify soft delete (not hard delete)
        division.refresh_from_db()
        assert division.is_active is False
        assert division.deleted_at is not None

    def test_delete_division_with_children_fails(self):
        """Test cannot delete division with active children"""
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
        
        # Setup: Create parent and child
        parent = Division.objects.create(
            code='HR',
            name='HR Department',
            level=0
        )
        child = Division.objects.create(
            code='HR-REC',
            name='HR Recruitment',
            parent=parent,
            level=1
        )
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Try to delete parent with active child
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': parent.id})
        response = client.delete(url)
        
        # Assert: Should fail
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'sub-divisions' in str(response.data['detail']).lower()

    def test_delete_division_with_employees_fails(self):
        """Test cannot delete division with active employees"""
        # Setup: Create admin user
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            employee_id='EMP999',
            phone='081234567890'
        )
        
        # Setup: Create division
        division = Division.objects.create(
            code='HR',
            name='HR Department',
            level=0
        )
        
        # Setup: Create employee in division
        employee = User.objects.create_user(
            username='employee',
            email='employee@example.com',
            password='emp123',
            first_name='Employee',
            last_name='User',
            employee_id='EMP001',
            phone='081234567891',
            division=division,
            is_active=True
        )
        
        # Setup: Authenticate as admin
        client = APIClient()
        client.force_authenticate(user=admin)
        
        # Act: Try to delete division with active employees
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        response = client.delete(url)
        
        # Assert: Should fail
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'employees' in str(response.data['detail']).lower()
