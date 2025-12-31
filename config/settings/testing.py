# config/settings/testing.py
"""
Testing-specific settings.

Fast, in-memory database for tests.
"""

from .base import *

# ========================================
# DEBUG
# ========================================
DEBUG = False

# ========================================
# TESTING FLAGS
# ========================================
TESTING = True

# ========================================
# DATABASE (In-memory SQLite for speed)
# ========================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# ========================================
# PASSWORD HASHERS (Faster for tests)
# ========================================
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# ========================================
# EMAIL (Memory backend for tests)
# ========================================
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# ========================================
# LOGGING (Minimal for tests)
# ========================================
LOGGING['root']['level'] = 'CRITICAL'
LOGGING['loggers']['django']['level'] = 'CRITICAL'
LOGGING['loggers']['apps']['level'] = 'CRITICAL'

print("✅ Testing settings loaded")