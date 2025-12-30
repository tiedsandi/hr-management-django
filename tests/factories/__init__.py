"""
Test Factories untuk membuat test data.
Menggunakan factory_boy untuk generate dummy data yang konsisten.
"""
from .division import DivisionFactory
from .user import UserFactory

__all__ = [
    'UserFactory',
    'DivisionFactory',
]
