"""
Tests for Division List & Create API

Endpoints:
- GET /api/v1/divisions/ - List divisions
- POST /api/v1/divisions/ - Create division
- GET /api/v1/divisions/tree/ - Get hierarchy tree
"""
import pytest
from django.urls import reverse
from rest_framework import status

from tests.factories import DivisionFactory, UserFactory


@pytest.mark.django_db
class TestDivisionListAPI:
    """Test division list endpoint"""
    
    def test_list_divisions_authenticated(self, authenticated_client):
        """Test listing divisions when authenticated"""
        # Create test data
        DivisionFactory.create_batch(3)
        
        url = reverse('api:v1:accounts:division-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
    
    def test_list_divisions_unauthenticated(self, api_client):
        """Test listing divisions requires authentication"""
        url = reverse('api:v1:accounts:division-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_divisions_with_search(self, authenticated_client):
        """Test search by name or code"""
        DivisionFactory(name='HR Department', code='HR')
        DivisionFactory(name='IT Department', code='IT')
        DivisionFactory(name='Finance Department', code='FIN')
        
        url = reverse('api:v1:accounts:division-list')
        response = authenticated_client.get(url, {'search': 'HR'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['code'] == 'HR'
    
    def test_list_divisions_filter_by_level(self, authenticated_client):
        """Test filter divisions by level"""
        parent = DivisionFactory(level=0)
        DivisionFactory(parent=parent)  # Level 1
        DivisionFactory(parent=parent)  # Level 1
        
        url = reverse('api:v1:accounts:division-list')
        
        # Filter level 0 (top level)
        response = authenticated_client.get(url, {'level': 0})
        assert len(response.data['results']) == 1
        
        # Filter level 1 (sub divisions)
        response = authenticated_client.get(url, {'level': 1})
        assert len(response.data['results']) == 2
    
    def test_list_divisions_top_only(self, authenticated_client):
        """Test filter top-level divisions only"""
        DivisionFactory.create_batch(2, parent=None)  # Top level
        parent = DivisionFactory(parent=None)
        DivisionFactory.create_batch(3, parent=parent)  # Children
        
        url = reverse('api:v1:accounts:division-list')
        response = authenticated_client.get(url, {'top_only': 'true'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3  # Only top-level
    
    def test_list_divisions_includes_employee_count(self, authenticated_client, division):
        """Test response includes employee count"""
        # Create employees in division
        UserFactory.create_batch(3, division=division, is_active=True)
        
        url = reverse('api:v1:accounts:division-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['employee_count'] == 3


@pytest.mark.django_db
class TestDivisionCreateAPI:
    """Test division creation endpoint"""
    
    def test_create_division_success(self, authenticated_client):
        """Test creating a new top-level division"""
        url = reverse('api:v1:accounts:division-list')
        data = {
            'code': 'HR',
            'name': 'HR Department',
            'description': 'Human Resources Department',
            'parent': None,
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == 'HR'
        assert response.data['name'] == 'HR Department'
        assert response.data['level'] == 0
    
    def test_create_sub_division_success(self, authenticated_client, division):
        """Test creating a sub-division with parent"""
        url = reverse('api:v1:accounts:division-list')
        data = {
            'code': 'HR-MGR',
            'name': 'HR Manager',
            'parent': division.id,
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == 'HR-MGR'
        assert response.data['parent'] == division.id
    
    def test_create_division_duplicate_code(self, authenticated_client):
        """Test creating division with duplicate code fails"""
        DivisionFactory(code='HR')
        
        url = reverse('api:v1:accounts:division-list')
        data = {
            'code': 'HR',
            'name': 'Another HR',
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_division_code_uppercase(self, authenticated_client):
        """Test code is automatically converted to uppercase"""
        url = reverse('api:v1:accounts:division-list')
        data = {
            'code': 'hr-dept',
            'name': 'HR Department',
            'parent': None,
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == 'HR-DEPT'
    
    def test_create_division_invalid_code(self, authenticated_client):
        """Test creating division with invalid code format"""
        url = reverse('api:v1:accounts:division-list')
        data = {
            'code': 'HR DEPT!',  # Spaces and special chars not allowed
            'name': 'HR Department',
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_division_missing_required_fields(self, authenticated_client):
        """Test creating division without required fields"""
        url = reverse('api:v1:accounts:division-list')
        data = {'code': 'HR'}  # Missing name
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data
    
    def test_create_division_unauthenticated(self, api_client):
        """Test creating division requires authentication"""
        url = reverse('api:v1:accounts:division-list')
        data = {
            'code': 'HR',
            'name': 'HR Department',
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDivisionTreeAPI:
    """Test division tree hierarchy endpoint"""
    
    def test_get_division_tree(self, authenticated_client):
        """Test getting full division hierarchy tree"""
        # Create hierarchy: HR -> HR-MGR -> HR-RECRUIT
        hr = DivisionFactory(code='HR', name='HR Department')
        hr_mgr = DivisionFactory(code='HR-MGR', name='HR Manager', parent=hr)
        hr_recruit = DivisionFactory(code='HR-RECRUIT', name='HR Recruitment', parent=hr_mgr)
        
        # Create another top-level
        it = DivisionFactory(code='IT', name='IT Department')
        
        url = reverse('api:v1:accounts:division-tree')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2  # 2 top-level divisions
        assert 'tree' in response.data
        
        # Verify tree structure
        tree = response.data['tree']
        hr_tree = next(d for d in tree if d['code'] == 'HR')
        assert len(hr_tree['children']) == 1
        assert hr_tree['children'][0]['code'] == 'HR-MGR'
    
    def test_get_division_tree_empty(self, authenticated_client):
        """Test getting tree when no divisions exist"""
        url = reverse('api:v1:accounts:division-tree')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['tree'] == []


@pytest.mark.django_db
class TestDivisionIntegration:
    """Integration tests for division list/create workflows"""
    
    def test_create_and_list_division(self, authenticated_client):
        """Test creating division and then listing it"""
        # Create
        url = reverse('api:v1:accounts:division-list')
        data = {
            'code': 'HR',
            'name': 'HR Department',
            'description': 'Human Resources',
            'parent': None,
        }
        create_response = authenticated_client.post(url, data, format='json')
        assert create_response.status_code == status.HTTP_201_CREATED
        division_id = create_response.data['id']
        
        # List and verify
        list_response = authenticated_client.get(url)
        assert list_response.status_code == status.HTTP_200_OK
        assert len(list_response.data['results']) == 1
        assert list_response.data['results'][0]['id'] == division_id
    
    def test_create_hierarchy_and_get_tree(self, authenticated_client):
        """Test creating hierarchy and retrieving as tree"""
        url = reverse('api:v1:accounts:division-list')
        
        # Create parent
        parent_data = {'code': 'HR', 'name': 'HR Department', 'parent': None}
        parent_response = authenticated_client.post(url, parent_data, format='json')
        parent_id = parent_response.data['id']
        
        # Create child
        child_data = {'code': 'HR-MGR', 'name': 'HR Manager', 'parent': parent_id}
        child_response = authenticated_client.post(url, child_data, format='json')
        
        # Get tree
        tree_url = reverse('api:v1:accounts:division-tree')
        tree_response = authenticated_client.get(tree_url)
        
        assert tree_response.status_code == status.HTTP_200_OK
        assert tree_response.data['count'] == 1
        assert len(tree_response.data['tree'][0]['children']) == 1
