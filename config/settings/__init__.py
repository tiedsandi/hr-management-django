"""
Settings package initialization.

Auto-imports settings based on DJANGO_ENV environment variable:
- development (default)
- production
- testing

Usage:
    export DJANGO_ENV=production
    python manage.py runserver
"""
import os

# Get environment (default: development)
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development')

# Import appropriate settings
if DJANGO_ENV == 'production':
    from .production import *
elif DJANGO_ENV == 'testing':
    from .testing import *
else:
    from .development import *

# Print current environment (for debugging)
print(f"🚀 Django Environment: {DJANGO_ENV.upper()}")