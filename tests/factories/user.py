"""
Factory untuk User model.
"""
import factory
from factory.django import DjangoModelFactory

from apps.accounts.models import User

from .division import DivisionFactory


class UserFactory(DjangoModelFactory):
    """Factory untuk membuat User test data"""
    
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    # Basic auth fields
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    
    # Employee fields
    employee_id = factory.Sequence(lambda n: f'EMP{n:04d}')
    phone = factory.Sequence(lambda n: f'08123456{n:04d}')
    division = None  # Optional, bisa diisi manual
    hire_date = factory.Faker('date_this_decade')
    type_of_employment = 'full_time'
    status = 'active'
    
    # User status
    is_active = True
    is_staff = False
    is_superuser = False
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override untuk handle password hashing"""
        # Pop password atau gunakan default
        password = kwargs.pop('password', None)
        if password is None:
            password = 'password123'
        
        # Create user tanpa password dulu
        user = model_class(**kwargs)
        user.set_password(password)
        user.save()
        return user


class UserWithDivisionFactory(UserFactory):
    """Factory untuk User dengan Division"""
    
    division = factory.SubFactory(DivisionFactory)


class StaffUserFactory(UserFactory):
    """Factory untuk Staff User"""
    
    is_staff = True


class SuperUserFactory(UserFactory):
    """Factory untuk Superuser"""
    
    is_staff = True
    is_superuser = True
    username = factory.Sequence(lambda n: f'admin{n}')
    email = factory.Faker('email')
