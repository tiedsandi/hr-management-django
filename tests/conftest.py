"""
Global pytest fixtures dan konfigurasi.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from tests.factories import DivisionFactory, UserFactory

User = get_user_model()


@pytest.fixture
def api_client():
    """
    DRF API client untuk testing endpoints.
    
    Usage:
        def test_endpoint(api_client):
            response = api_client.get('/api/v1/accounts/profile/')
    """
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """
    API client yang sudah authenticated dengan user biasa.
    
    Usage:
        def test_protected_endpoint(authenticated_client):
            response = authenticated_client.get('/api/v1/accounts/profile/')
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """
    API client yang sudah authenticated dengan admin user.
    
    Usage:
        def test_admin_endpoint(admin_client):
            response = admin_client.get('/api/v1/admin/users/')
    """
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def user():
    """
    User biasa untuk testing (tanpa division).
    Password default: 'password123'
    
    Usage:
        def test_user_login(user):
            assert user.check_password('password123')
    """
    return UserFactory()


@pytest.fixture
def user_with_division():
    """
    User dengan division untuk testing relasi.
    
    Usage:
        def test_user_has_division(user_with_division):
            assert user_with_division.division is not None
    """
    division = DivisionFactory()
    return UserFactory(division=division)


@pytest.fixture
def admin_user():
    """
    Superuser untuk testing admin endpoints.
    
    Usage:
        def test_admin_access(admin_user):
            assert admin_user.is_superuser
    """
    return UserFactory(
        username='admin',
        email='admin@example.com',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def division():
    """
    Division untuk testing.
    
    Usage:
        def test_division_creation(division):
            assert division.level == 0
    """
    return DivisionFactory()


@pytest.fixture
def sub_division(division):
    """
    Sub-division dengan parent.
    
    Usage:
        def test_sub_division(sub_division):
            assert sub_division.parent is not None
    """
    return DivisionFactory(parent=division)


# Database settings
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Enable database access untuk semua tests.
    Dengan autouse=True, tidak perlu tambahkan @pytest.mark.django_db di setiap test.
    """
    pass
