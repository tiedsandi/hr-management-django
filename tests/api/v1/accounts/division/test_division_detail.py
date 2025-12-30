"""
Tests for Division Detail, Update, Delete API

Endpoints:
- GET /api/v1/divisions/{id}/ - Get division detail
- PUT /api/v1/divisions/{id}/ - Update division (full)
- PATCH /api/v1/divisions/{id}/ - Update division (partial)
- DELETE /api/v1/divisions/{id}/ - Delete division
"""
import pytest
from django.urls import reverse
from rest_framework import status

from apps.accounts.models import Division
from tests.factories import DivisionFactory, UserFactory


@pytest.mark.django_db
class TestDivisionDetailAPI:
    """Test division detail endpoint"""
    
    def test_get_division_detail(self, authenticated_client, division):
        """Test getting division detail"""
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == division.id
        assert response.data['code'] == division.code
        assert response.data['name'] == division.name
        assert 'full_path' in response.data
        assert 'employee_count' in response.data
        assert 'total_employee_count' in response.data
    
    def test_get_division_detail_with_hierarchy(self, authenticated_client):
        """Test detail includes children and ancestors"""
        # Create hierarchy
        grandparent = DivisionFactory(code='HR', name='HR Department')
        parent = DivisionFactory(code='HR-MGR', name='HR Manager', parent=grandparent)
        child = DivisionFactory(code='HR-RECRUIT', name='HR Recruitment', parent=parent)
        
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': parent.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['children']) == 1
        assert response.data['children'][0]['code'] == 'HR-RECRUIT'
        assert len(response.data['ancestors']) == 1
        assert response.data['ancestors'][0]['code'] == 'HR'
    
    def test_get_division_detail_not_found(self, authenticated_client):
        """Test getting non-existent division"""
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': 99999})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_division_detail_unauthenticated(self, api_client, division):
        """Test detail requires authentication"""
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDivisionUpdateAPI:
    """Test division update endpoints"""
    
    def test_update_division_full(self, authenticated_client, division):
        """Test full update (PUT) of division"""
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        data = {
            'code': 'HR-UPDATED',
            'name': 'Updated HR Department',
            'description': 'Updated description',
        }
        response = authenticated_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 'HR-UPDATED'
        assert response.data['name'] == 'Updated HR Department'
        
        # Verify database updated
        division.refresh_from_db()
        assert division.code == 'HR-UPDATED'
    
    def test_update_division_partial(self, authenticated_client, division):
        """Test partial update (PATCH) of division"""
        original_code = division.code
        
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        data = {'name': 'Partially Updated Name'}
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Partially Updated Name'
        assert response.data['code'] == original_code  # Should remain unchanged
    
    def test_update_division_change_parent(self, authenticated_client):
        """Test changing division parent"""
        old_parent = DivisionFactory(code='HR')
        new_parent = DivisionFactory(code='IT')
        division = DivisionFactory(code='SHARED', parent=old_parent)
        
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        data = {'parent': new_parent.id}
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['parent'] == new_parent.id
        
        # Verify level updated
        division.refresh_from_db()
        assert division.parent == new_parent
        assert division.level == 1
    
    def test_update_division_remove_parent(self, authenticated_client):
        """Test removing parent (move to top level)"""
        parent = DivisionFactory()
        division = DivisionFactory(parent=parent)
        
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        data = {'parent': None}
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['parent'] is None
        
        division.refresh_from_db()
        assert division.level == 0
    
    def test_update_division_circular_reference(self, authenticated_client):
        """Test cannot set child as parent (circular reference)"""
        parent = DivisionFactory(code='PARENT')
        child = DivisionFactory(code='CHILD', parent=parent)
        
        # Try to set child as parent
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': parent.id})
        data = {'parent': child.id}
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_update_division_self_as_parent(self, authenticated_client, division):
        """Test cannot set self as parent"""
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        data = {'parent': division.id}
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_update_division_code_to_duplicate(self, authenticated_client):
        """Test cannot update code to existing code"""
        DivisionFactory(code='EXISTING')
        division = DivisionFactory(code='MYCODE')
        
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        data = {'code': 'EXISTING'}
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_update_division_unauthenticated(self, api_client, division):
        """Test update requires authentication"""
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        data = {'name': 'New Name'}
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDivisionDeleteAPI:
    """Test division delete endpoint"""
    
    def test_delete_division_success(self, authenticated_client, division):
        """Test soft deleting a division"""
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify soft delete
        division.refresh_from_db()
        assert division.deleted_at is not None
    
    def test_delete_division_with_children(self, authenticated_client):
        """Test cannot delete division with active children"""
        parent = DivisionFactory()
        DivisionFactory(parent=parent)  # Active child
        
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': parent.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'sub-divisions' in str(response.data)
    
    def test_delete_division_with_employees(self, authenticated_client, division):
        """Test cannot delete division with active employees"""
        UserFactory(division=division, is_active=True)
        
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'employees' in str(response.data)
    
    def test_delete_division_unauthenticated(self, api_client, division):
        """Test delete requires authentication"""
        url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDivisionIntegration:
    """Integration tests for division detail/update/delete workflows"""
    
    def test_create_update_delete_flow(self, authenticated_client):
        """Test complete CRUD flow"""
        # Create
        list_url = reverse('api:v1:accounts:division-list')
        create_data = {'code': 'TEST', 'name': 'Test Division', 'parent': None}
        create_response = authenticated_client.post(list_url, create_data, format='json')
        assert create_response.status_code == status.HTTP_201_CREATED
        division_id = create_response.data['id']
        
        # Get detail
        detail_url = reverse('api:v1:accounts:division-detail', kwargs={'pk': division_id})
        get_response = authenticated_client.get(detail_url)
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.data['code'] == 'TEST'
        
        # Update
        update_data = {'name': 'Updated Test Division'}
        update_response = authenticated_client.patch(detail_url, update_data, format='json')
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data['name'] == 'Updated Test Division'
        
        # Delete
        delete_response = authenticated_client.delete(detail_url)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deleted (should return 404)
        get_after_delete = authenticated_client.get(detail_url)
        assert get_after_delete.status_code == status.HTTP_404_NOT_FOUND
    
    def test_hierarchy_update_cascade(self, authenticated_client):
        """Test updating parent updates child levels"""
        # Create hierarchy: L0 -> L1 -> L2
        l0 = DivisionFactory(code='L0')
        l1_response = authenticated_client.post(
            reverse('api:v1:accounts:division-list'),
            {'code': 'L1', 'name': 'Level 1', 'parent': l0.id},
            format='json'
        )
        l1_id = l1_response.data['id']
        
        l2_response = authenticated_client.post(
            reverse('api:v1:accounts:division-list'),
            {'code': 'L2', 'name': 'Level 2', 'parent': l1_id},
            format='json'
        )
        
        # Verify levels
        assert l1_response.data['level'] == 1
        assert l2_response.data['level'] == 2
        
        # Move L1 to top level
        authenticated_client.patch(
            reverse('api:v1:accounts:division-detail', kwargs={'pk': l1_id}),
            {'parent': None},
            format='json'
        )
        
        # Verify L1 is now level 0
        l1_updated = Division.objects.get(id=l1_id)
        assert l1_updated.level == 0
