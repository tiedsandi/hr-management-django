"""
Development settings.
"""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# CORS - Allow all for development
CORS_ALLOW_ALL_ORIGINS = True

# Email - Console backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Security - Relaxed
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Jazzmin
JAZZMIN_SETTINGS['show_ui_builder'] = True

# Logging
LOGGING['loggers']['apps']['level'] = 'DEBUG'

print("✅ Development settings loaded")