```
# Testing Documentation

## 📋 Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Global fixtures & configuration
├── pytest.ini                  # Pytest settings
├── factories/                  # Test data factories
│   ├── __init__.py
│   ├── user.py                # User factory
│   └── division.py            # Division factory
├── api/                       # API endpoint tests
│   └── v1/
│       └── accounts/
│           ├── test_login.py
│           ├── test_refresh.py
│           ├── test_profile.py
│           └── test_register_logout.py
└── core/                      # Core utilities tests
    ├── utils/
    │   ├── test_datetime.py
    │   └── test_formatting.py
    └── validators/
        └── test_validators.py
```

## 🚀 Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=apps --cov=api --cov-report=html

# Parallel execution (faster)
pytest -n auto

# Stop on first failure
pytest -x

# Verbose output
pytest -v

# Show print statements
pytest -s
```

### Run Specific Tests

```bash
# Specific folder
pytest tests/api/
pytest tests/core/

# Specific file
pytest tests/api/v1/accounts/test_login.py

# Specific class
pytest tests/api/v1/accounts/test_login.py::TestLoginAPI

# Specific test function
pytest tests/api/v1/accounts/test_login.py::TestLoginAPI::test_login_success
```

### Test Markers

```bash
# Run by marker
pytest -m unit              # Unit tests only
pytest -m api               # API tests only
pytest -m integration       # Integration tests
pytest -m security          # Security tests
pytest -m "not slow"        # Exclude slow tests
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=apps --cov=api --cov-report=html

# Open coverage report
open htmlcov/index.html

# Terminal coverage with details
pytest --cov=apps --cov-report=term-missing

# Coverage with specific threshold
pytest --cov=apps --cov-fail-under=80
```

## 🏭 Factories (Test Data Generation)

Factories use `factory_boy` to generate consistent test data automatically.

### UserFactory

```python
from tests.factories import UserFactory

# Basic user (password: 'password123')
user = UserFactory()

# User with custom data
user = UserFactory(
    username='john',
    email='john@example.com',
    first_name='John'
)

# User with division
from tests.factories import DivisionFactory
division = DivisionFactory()
user = UserFactory(division=division)

# Or use UserWithDivisionFactory
user = UserWithDivisionFactory()

# Create multiple users
users = UserFactory.create_batch(5)

# Superuser
admin = SuperUserFactory()
```

### DivisionFactory

```python
from tests.factories import DivisionFactory, SubDivisionFactory

# Top-level division
division = DivisionFactory()

# Sub-division with parent
sub_div = SubDivisionFactory()

# Or manually
sub_div = DivisionFactory(parent=division)
```

## 🎯 Fixtures

Global fixtures are available in `conftest.py`.

### Available Fixtures

#### API Clients
- `api_client` - Basic DRF API client
- `authenticated_client` - Client with authenticated user
- `admin_client` - Client with admin user

#### Users
- `user` - Regular user (no division)
- `user_with_division` - User with division
- `admin_user` - Superuser

#### Others
- `division` - Division object
- `sub_division` - Sub-division with parent

### Usage Examples

```python
def test_get_profile(authenticated_client, user):
    """Test with authenticated client"""
    response = authenticated_client.get('/api/v1/accounts/profile/')
    assert response.status_code == 200
    assert response.data['username'] == user.username

def test_admin_endpoint(admin_client):
    """Test admin-only endpoint"""
    response = admin_client.get('/api/v1/admin/users/')
    assert response.status_code == 200

def test_create_with_factory():
    """Test using factory directly"""
    user = UserFactory()
    assert user.check_password('password123')
```

## 📝 Test Markers

Use markers to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_model_method():
    """Fast, isolated unit test"""
    pass

@pytest.mark.integration
def test_login_flow(api_client, user):
    """Test multiple components together"""
    pass

@pytest.mark.slow
def test_external_api():
    """Slow test (e.g., external API calls)"""
    pass

@pytest.mark.api
def test_endpoint(authenticated_client):
    """API endpoint test"""
    pass
```

## ✅ Best Practices

### 1. Naming Convention
- Files: `test_*.py`
- Classes: `Test*`
- Functions: `test_*`

### 2. AAA Pattern (Arrange-Act-Assert)

```python
def test_user_full_name():
    # Arrange - Setup
    user = UserFactory(first_name='John', last_name='Doe')
    
    # Act - Execute
    result = user.get_full_name()
    
    # Assert - Verify
    assert result == "John Doe"
```

### 3. Use Factories, Not Manual Creation

```python
# ❌ Bad - Manual creation
user = User.objects.create(
    username='test',
    email='test@example.com',
    employee_id='EMP001',
    ...
)

# ✅ Good - Use factory
user = UserFactory()
```

### 4. Test One Thing at a Time

```python
# ❌ Bad - Testing multiple things
def test_user():
    user = UserFactory()
    assert user.username
    assert user.email
    response = client.get(f'/api/users/{user.id}/')
    assert response.status_code == 200

# ✅ Good - Separate tests
def test_user_has_username():
    user = UserFactory()
    assert user.username

def test_get_user_api_returns_200():
    user = UserFactory()
    response = client.get(f'/api/users/{user.id}/')
    assert response.status_code == 200
```

### 5. Descriptive Test Names

```python
# ❌ Bad - Unclear purpose
def test_login():
    pass

# ✅ Good - Clear intent
def test_login_success_with_valid_credentials():
    pass

def test_login_fails_with_wrong_password():
    pass

def test_login_fails_with_inactive_user():
    pass
```

### 6. Don't Test Framework Code

```python
# ❌ Bad - Testing Django functionality
def test_user_save():
    user = User(username='test')
    user.save()
    assert User.objects.filter(username='test').exists()

# ✅ Good - Test your custom logic
def test_user_full_name_property():
    user = UserFactory()
    expected = f"{user.first_name} {user.last_name}"
    assert user.full_name == expected
```

## 🔍 Debugging Tests

### Run Last Failed Tests

```bash
pytest --lf
```

### Run Failed Tests First

```bash
pytest --ff
```

### Show Local Variables on Failure

```bash
pytest -l
```

### Use PDB Debugger

```python
def test_something():
    user = UserFactory()
    import pdb; pdb.set_trace()  # Breakpoint here
    assert user.username
```

### Print Statement Debugging

```bash
# Show print outputs
pytest -s

# Or use pytest's print
def test_something():
    user = UserFactory()
    print(f"User: {user.username}")  # Will show with -s flag
```

## 📊 Coverage Requirements

**Target Coverage: 80% minimum**

### Check Coverage

```bash
# Generate report
pytest --cov=apps --cov=api --cov-report=term-missing

# Fail if below threshold
pytest --cov=apps --cov-fail-under=80

# Generate HTML report
pytest --cov=apps --cov-report=html
open htmlcov/index.html
```

### Coverage Configuration

Located in `pytest.ini`:
```ini
[pytest]
addopts = 
    --cov=apps
    --cov=api
    --cov-report=html
    --cov-report=term-missing:skip-covered
```

## 🐛 Troubleshooting

### Database Locked Error

```bash
# Remove test database
rm db.sqlite3

# Or force recreate
pytest --create-db
```

### Import Errors

```bash
# Ensure you're in project root
cd /home/fe/Desktop/hr-managements

# Activate virtual environment
source venv/bin/activate

# Verify Python path
python -c "import sys; print(sys.path)"
```

### Fixtures Not Found

```bash
# Check conftest.py location
# Should be in tests/ directory

# Check pytest discovery
pytest --collect-only
```

### Parallel Tests Issues

```bash
# Run without parallel
pytest

# Or limit workers
pytest -n 2
```

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [factory_boy Documentation](https://factoryboy.readthedocs.io/)
- [DRF Testing Guide](https://www.django-rest-framework.org/api-guide/testing/)
- [Django Testing Documentation](https://docs.djangoproject.com/en/4.2/topics/testing/)

## 🎯 Quick Reference

```bash
# Development workflow
pytest -x -v                    # Stop on first failure, verbose
pytest -n auto                  # Run parallel
pytest --lf                     # Re-run last failures
pytest -m "not slow"           # Skip slow tests

# Before commit
pytest --cov=apps --cov-fail-under=80

# CI/CD
pytest -n auto --cov=apps --cov-report=xml

```