"""
Admin registration untuk accounts app
"""
from .division import DivisionAdmin
from .user import UserAdmin

# Django auto-discover akan pick up registrations dari submodules
__all__ = ['DivisionAdmin', 'UserAdmin']