"""
Tests for Division Custom Actions API

Endpoints:
- GET /api/v1/divisions/{id}/children/ - Get children divisions
- GET /api/v1/divisions/{id}/ancestors/ - Get ancestor divisions
- GET /api/v1/divisions/{id}/employees/ - Get employees in division
"""
import pytest
from django.urls import reverse
from rest_framework import status

from tests.factories import DivisionFactory, UserFactory


@pytest.mark.django_db
class TestDivisionChildrenAPI:
    """Test division children endpoint"""
    
    def test_get_division_children(self, authenticated_client):
        """Test getting immediate children of a division"""
        parent = DivisionFactory(code='PARENT')
        child1 = DivisionFactory(code='CHILD1', parent=parent)
        child2 = DivisionFactory(code='CHILD2', parent=parent)
        
        # Create grandchild (should not be included)
        DivisionFactory(code='GRANDCHILD', parent=child1)
        
        url = reverse('api:v1:accounts:division-children', kwargs={'pk': parent.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert len(response.data['results']) == 2
        
        codes = [r['code'] for r in response.data['results']]
        assert 'CHILD1' in codes
        assert 'CHILD2' in codes
        assert 'GRANDCHILD' not in codes  # Only immediate children
    
    def test_get_division_children_empty(self, authenticated_client, division):
        """Test getting children when division has no children"""
        url = reverse('api:v1:accounts:division-children', kwargs={'pk': division.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['results'] == []
    
    def test_get_division_children_unauthenticated(self, api_client, division):
        """Test children endpoint requires authentication"""
        url = reverse('api:v1:accounts:division-children', kwargs={'pk': division.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDivisionAncestorsAPI:
    """Test division ancestors endpoint"""
    
    def test_get_division_ancestors(self, authenticated_client):
        """Test getting all ancestor divisions"""
        # Create hierarchy: L0 -> L1 -> L2
        l0 = DivisionFactory(code='L0', name='Level 0')
        l1 = DivisionFactory(code='L1', name='Level 1', parent=l0)
        l2 = DivisionFactory(code='L2', name='Level 2', parent=l1)
        
        url = reverse('api:v1:accounts:division-ancestors', kwargs={'pk': l2.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        # Verify ancestors order (bottom to top)
        codes = [r['code'] for r in response.data['results']]
        assert codes[0] == 'L1'  # Direct parent first
        assert codes[1] == 'L0'  # Then grandparent
    
    def test_get_division_ancestors_top_level(self, authenticated_client, division):
        """Test top-level division has no ancestors"""
        url = reverse('api:v1:accounts:division-ancestors', kwargs={'pk': division.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['results'] == []
    
    def test_get_division_ancestors_unauthenticated(self, api_client, division):
        """Test ancestors endpoint requires authentication"""
        url = reverse('api:v1:accounts:division-ancestors', kwargs={'pk': division.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDivisionEmployeesAPI:
    """Test division employees endpoint"""
    
    def test_get_division_employees(self, authenticated_client, division):
        """Test getting employees in division"""
        # Create employees
        emp1 = UserFactory(division=division, is_active=True, employee_id='EMP001')
        emp2 = UserFactory(division=division, is_active=True, employee_id='EMP002')
        
        # Inactive employee should not be included
        UserFactory(division=division, is_active=False)
        
        url = reverse('api:v1:accounts:division-employees', kwargs={'pk': division.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert response.data['division'] == division.name
        assert response.data['include_children'] is False
        
        emp_ids = [e['employee_id'] for e in response.data['results']]
        assert 'EMP001' in emp_ids
        assert 'EMP002' in emp_ids
    
    def test_get_division_employees_include_children(self, authenticated_client):
        """Test getting employees including from child divisions"""
        # Create hierarchy
        parent = DivisionFactory(code='PARENT')
        child = DivisionFactory(code='CHILD', parent=parent)
        
        # Create employees
        parent_emp = UserFactory(division=parent, is_active=True, employee_id='P001')
        child_emp = UserFactory(division=child, is_active=True, employee_id='C001')
        
        url = reverse('api:v1:accounts:division-employees', kwargs={'pk': parent.id})
        response = authenticated_client.get(url, {'include_children': 'true'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert response.data['include_children'] is True
        
        emp_ids = [e['employee_id'] for e in response.data['results']]
        assert 'P001' in emp_ids
        assert 'C001' in emp_ids
    
    def test_get_division_employees_empty(self, authenticated_client, division):
        """Test getting employees when division has no employees"""
        url = reverse('api:v1:accounts:division-employees', kwargs={'pk': division.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['results'] == []
    
    def test_get_division_employees_unauthenticated(self, api_client, division):
        """Test employees endpoint requires authentication"""
        url = reverse('api:v1:accounts:division-employees', kwargs={'pk': division.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDivisionCustomActionsIntegration:
    """Integration tests for division custom actions"""
    
    def test_hierarchy_navigation(self, authenticated_client):
        """Test navigating hierarchy using children and ancestors"""
        # Create 3-level hierarchy
        l0 = DivisionFactory(code='L0')
        l1 = DivisionFactory(code='L1', parent=l0)
        l2 = DivisionFactory(code='L2', parent=l1)
        
        # Get L1's children
        children_url = reverse('api:v1:accounts:division-children', kwargs={'pk': l1.id})
        children_response = authenticated_client.get(children_url)
        assert children_response.data['count'] == 1
        assert children_response.data['results'][0]['code'] == 'L2'
        
        # Get L1's ancestors
        ancestors_url = reverse('api:v1:accounts:division-ancestors', kwargs={'pk': l1.id})
        ancestors_response = authenticated_client.get(ancestors_url)
        assert ancestors_response.data['count'] == 1
        assert ancestors_response.data['results'][0]['code'] == 'L0'
    
    def test_employee_distribution_across_hierarchy(self, authenticated_client):
        """Test employee distribution in hierarchical divisions"""
        # Create hierarchy
        parent = DivisionFactory(code='PARENT')
        child1 = DivisionFactory(code='CHILD1', parent=parent)
        child2 = DivisionFactory(code='CHILD2', parent=parent)
        
        # Distribute employees
        UserFactory.create_batch(2, division=parent, is_active=True)
        UserFactory.create_batch(3, division=child1, is_active=True)
        UserFactory.create_batch(4, division=child2, is_active=True)
        
        # Get parent employees only
        url = reverse('api:v1:accounts:division-employees', kwargs={'pk': parent.id})
        response_only = authenticated_client.get(url)
        assert response_only.data['count'] == 2
        
        # Get parent employees with children
        response_all = authenticated_client.get(url, {'include_children': 'true'})
        assert response_all.data['count'] == 9  # 2 + 3 + 4
