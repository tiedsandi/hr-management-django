"""
Testing settings.
"""
from .base import *

DEBUG = False
TESTING = True

# Database - In-memory SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Password hashers - Fast
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Email - Memory backend
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Logging - Minimal
LOGGING['root']['level'] = 'CRITICAL'
LOGGING['loggers']['django']['level'] = 'CRITICAL'
LOGGING['loggers']['apps']['level'] = 'CRITICAL'

print("✅ Testing settings loaded")