# Simplified Division API Tests

This folder contains example tests using the **simplified approach** for Division API testing.

## What is the Simplified Approach?

Each test:
- ✅ Sets up its own data using Django ORM directly
- ✅ Creates users with `User.objects.create_user()`
- ✅ Creates divisions with `Division.objects.create()`
- ✅ Authenticates with `client.force_authenticate()`
- ❌ No pytest fixtures
- ❌ No factory-boy
- ❌ No conftest.py

## File Structure

```
tests/simplified/division/
├── __init__.py                      # Package initialization
├── README.md                        # This file
├── test_division_list_simple.py     # List, Create, Tree endpoints
├── test_division_detail_simple.py   # Detail, Update, Delete endpoints
└── test_division_actions_simple.py  # Custom actions (children, ancestors, employees)
```

## Comparison with Comprehensive Approach

### Simplified (this folder)
```python
def test_create_division(self):
    # Setup: Create user manually (9 lines)
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
    
    # Act: Create division (6 lines)
    url = reverse('api:v1:accounts:division-list')
    data = {
        'code': 'HR',
        'name': 'HR Department',
        'parent': None,
    }
    response = client.post(url, data, format='json')
    
    # Assert: Check response (3 lines)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['code'] == 'HR'
```

**Total: ~18 lines per test**

### Comprehensive (tests/api/v1/accounts/division/)
```python
def test_create_division(self, authenticated_client):
    # Setup: Done by fixtures (0 lines)
    
    # Act: Create division (6 lines)
    url = reverse('api:v1:accounts:division-list')
    data = {
        'code': 'HR',
        'name': 'HR Department',
        'parent': None,
    }
    response = authenticated_client.post(url, data, format='json')
    
    # Assert: Check response (3 lines)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['code'] == 'HR'
```

**Total: ~9 lines per test**

## When to Use Simplified Approach?

### ✅ Good for:
- Quick prototypes
- Learning Django/DRF testing
- Small projects (<20 tests)
- One-off tests for debugging

### ❌ Not ideal for:
- Production applications
- Projects with 30+ tests
- Complex model relationships
- Team projects requiring maintenance

## Running These Tests

```bash
# Run all simplified division tests
pytest tests/simplified/division/

# Run specific test file
pytest tests/simplified/division/test_division_list_simple.py

# Run specific test class
pytest tests/simplified/division/test_division_list_simple.py::TestDivisionListSimple

# Run specific test method
pytest tests/simplified/division/test_division_list_simple.py::TestDivisionListSimple::test_list_divisions_authenticated
```

## Key Differences

| Aspect | Simplified | Comprehensive |
|--------|-----------|---------------|
| **Setup per test** | Manual (9-15 lines) | Fixtures (0 lines) |
| **Code duplication** | High | Low |
| **Maintenance** | Every test needs update | Update once in factory |
| **Readability** | All setup visible | Focus on test logic |
| **Learning curve** | Easy | Medium |
| **Test speed** | Same | Same |

## Example: Creating Division Hierarchy

### Simplified Way
```python
# Create each division manually
hr = Division.objects.create(code='HR', name='HR Department', level=0)
hr_mgr = Division.objects.create(
    code='HR-MGR',
    name='HR Management',
    parent=hr,
    level=1
)
hr_rec = Division.objects.create(
    code='HR-REC',
    name='HR Recruitment',
    parent=hr_mgr,
    level=2
)
```

**15 lines of setup code**

### Comprehensive Way (with factory)
```python
# Factory handles relationships automatically
division_tree = DivisionFactory.create_hierarchy(
    levels=['HR', 'HR-MGR', 'HR-REC']
)
```

**1 line of setup code**

## Test Coverage

These simplified tests cover:
- ✅ Division CRUD operations (Create, Read, Update, Delete)
- ✅ Division hierarchy (tree structure)
- ✅ Custom actions (children, ancestors, employees)
- ✅ Authentication requirements
- ✅ Validation rules
- ✅ Integration workflows

## Migration to Comprehensive

If you want to migrate these tests to comprehensive approach:

1. **Create factories** (once):
   - `tests/factories/division.py`

2. **Create fixtures** (once):
   - `tests/conftest.py` (add division fixtures)

3. **Refactor tests** (gradually):
   - Replace manual setup with fixtures
   - Remove `User.objects.create_user()` calls
   - Use `authenticated_client` fixture

See `COMPARISON.md` in parent folder for detailed migration guide.

## Related Files

- **Comprehensive version**: `tests/api/v1/accounts/division/`
- **User simplified tests**: `tests/simplified/user/`
- **Detailed comparison**: `tests/simplified/COMPARISON.md`
- **Factories used in comprehensive**: `tests/factories/`
- **Fixtures used in comprehensive**: `tests/conftest.py`

## Notes

⚠️ **These are example tests for comparison purposes.**

The actual comprehensive tests in `tests/api/v1/accounts/division/` are:
- More extensive (47 tests vs 20 tests here)
- Better maintained
- Production-ready

Use this folder to:
- Compare testing approaches
- Learn the differences
- Decide which approach to use for new features
- Train new team members
