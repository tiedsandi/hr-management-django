"""
Simplified Division Custom Actions API Tests

Compare with: tests/api/v1/accounts/division/test_division_actions.py
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Division, User


@pytest.mark.django_db
class TestDivisionChildrenSimple:
    """Division children endpoint tests - Simplified approach"""

    def test_get_division_children(self):
        """Test getting immediate children of a division"""
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
        
        # Setup: Create parent division
        parent = Division.objects.create(
            code='HR',
            name='HR Department',
            level=0
        )
        
        # Setup: Create children
        child1 = Division.objects.create(
            code='HR-REC',
            name='HR Recruitment',
            parent=parent,
            level=1
        )
        child2 = Division.objects.create(
            code='HR-TRA',
            name='HR Training',
            parent=parent,
            level=1
        )
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Get children
        url = reverse('api:v1:accounts:division-children', kwargs={'pk': parent.id})
        response = client.get(url)
        
        # Assert: Both children returned
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        codes = [r['code'] for r in response.data['results']]
        assert 'HR-REC' in codes
        assert 'HR-TRA' in codes

    def test_get_division_children_empty(self):
        """Test getting children when division has none"""
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
        
        # Setup: Create division without children
        division = Division.objects.create(
            code='HR',
            name='HR Department',
            level=0
        )
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Get children
        url = reverse('api:v1:accounts:division-children', kwargs={'pk': division.id})
        response = client.get(url)
        
        # Assert: Empty list
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert len(response.data['results']) == 0


@pytest.mark.django_db
class TestDivisionAncestorsSimple:
    """Division ancestors endpoint tests - Simplified approach"""

    def test_get_division_ancestors(self):
        """Test getting all ancestor divisions"""
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
        
        # Setup: Create hierarchy (3 levels)
        level0 = Division.objects.create(
            code='HR',
            name='HR Department',
            level=0
        )
        level1 = Division.objects.create(
            code='HR-MGR',
            name='HR Management',
            parent=level0,
            level=1
        )
        level2 = Division.objects.create(
            code='HR-REC',
            name='HR Recruitment',
            parent=level1,
            level=2
        )
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Act: Get ancestors of level2
        url = reverse('api:v1:accounts:division-ancestors', kwargs={'pk': level2.id})
        response = client.get(url)
        
        # Assert: Should return level0 and level1
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        codes = [a['code'] for a in response.data]
        assert 'HR' in codes
        assert 'HR-MGR' in codes


@pytest.mark.django_db
class TestDivisionEmployeesSimple:
    """Division employees endpoint tests - Simplified approach"""

    def test_get_division_employees(self):
        """Test getting employees in a division"""
        # Setup: Create admin user
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            employee_id='ADMIN001',
            phone='081234567890'
        )
        
        # Setup: Create division
        division = Division.objects.create(
            code='HR',
            name='HR Department',
            level=0
        )
        
        # Setup: Create employees in division
        emp1 = User.objects.create_user(
            username='emp1',
            email='emp1@example.com',
            password='emp123',
            first_name='Employee',
            last_name='One',
            employee_id='EMP001',
            phone='081234567891',
            division=division,
            is_active=True
        )
        emp2 = User.objects.create_user(
            username='emp2',
            email='emp2@example.com',
            password='emp123',
            first_name='Employee',
            last_name='Two',
            employee_id='EMP002',
            phone='081234567892',
            division=division,
            is_active=True
        )
        
        # Setup: Create inactive employee (should not appear)
        inactive = User.objects.create_user(
            username='inactive',
            email='inactive@example.com',
            password='emp123',
            first_name='Inactive',
            last_name='User',
            employee_id='EMP999',
            phone='081234567893',
            division=division,
            is_active=False
        )
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=admin)
        
        # Act: Get employees
        url = reverse('api:v1:accounts:division-employees', kwargs={'pk': division.id})
        response = client.get(url)
        
        # Assert: Only active employees returned
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert response.data['division'] == 'HR Department'
        
        employee_ids = [e['employee_id'] for e in response.data['employees']]
        assert 'EMP001' in employee_ids
        assert 'EMP002' in employee_ids
        assert 'EMP999' not in employee_ids  # Inactive not included

    def test_get_division_employees_include_children(self):
        """Test getting employees including from child divisions"""
        # Setup: Create admin user
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            employee_id='ADMIN001',
            phone='081234567890'
        )
        
        # Setup: Create hierarchy
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
        
        # Setup: Create employee in parent
        parent_emp = User.objects.create_user(
            username='parent_emp',
            email='parent@example.com',
            password='emp123',
            first_name='Parent',
            last_name='Employee',
            employee_id='P001',
            phone='081234567891',
            division=parent,
            is_active=True
        )
        
        # Setup: Create employee in child
        child_emp = User.objects.create_user(
            username='child_emp',
            email='child@example.com',
            password='emp123',
            first_name='Child',
            last_name='Employee',
            employee_id='C001',
            phone='081234567892',
            division=child,
            is_active=True
        )
        
        # Setup: Authenticate
        client = APIClient()
        client.force_authenticate(user=admin)
        
        # Act: Get employees including children
        url = reverse('api:v1:accounts:division-employees', kwargs={'pk': parent.id})
        response = client.get(url, {'include_children': 'true'})
        
        # Assert: Both parent and child employees returned
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        employee_ids = [e['employee_id'] for e in response.data['employees']]
        assert 'P001' in employee_ids
        assert 'C001' in employee_ids


@pytest.mark.django_db
class TestDivisionIntegrationSimple:
    """Integration tests - Simplified approach"""

    def test_complete_division_workflow(self):
        """Test complete workflow: create hierarchy, assign employees, query"""
        # Setup: Create admin user
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            employee_id='ADMIN001',
            phone='081234567890'
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        
        # Step 1: Create parent division
        url = reverse('api:v1:accounts:division-list')
        parent_data = {
            'code': 'HR',
            'name': 'HR Department',
            'description': 'Human Resources',
            'parent': None,
        }
        response = client.post(url, parent_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        parent_id = response.data['id']
        
        # Step 2: Create child division
        child_data = {
            'code': 'HR-REC',
            'name': 'HR Recruitment',
            'parent': parent_id,
        }
        response = client.post(url, child_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        child_id = response.data['id']
        
        # Step 3: Create employee in child division
        child_division = Division.objects.get(id=child_id)
        employee = User.objects.create_user(
            username='recruiter',
            email='recruiter@example.com',
            password='rec123',
            first_name='John',
            last_name='Recruiter',
            employee_id='REC001',
            phone='081234567891',
            division=child_division,
            is_active=True
        )
        
        # Step 4: Get parent detail (should show child)
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': parent_id})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['children']) == 1
        assert response.data['children'][0]['code'] == 'HR-REC'
        
        # Step 5: Get employees including children
        url = reverse('api:v1:accounts:division-employees', kwargs={'pk': parent_id})
        response = client.get(url, {'include_children': 'true'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['employees'][0]['employee_id'] == 'REC001'
        
        # Step 6: Get hierarchy tree
        url = reverse('api:v1:accounts:division-tree')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['tree'][0]['code'] == 'HR'
        assert len(response.data['tree'][0]['children']) == 1
