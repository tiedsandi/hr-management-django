# config/settings/development.py
"""
Development-specific settings.

These settings are optimized for local development.
NOT for production use!
"""

from .base import *

# ========================================
# DEBUG
# ========================================
DEBUG = True

# ========================================
# ALLOWED HOSTS
# ========================================
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# ========================================
# CORS (Allow all for development)
# ========================================
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# ========================================
# DATABASE (SQLite for development)
# ========================================
# Already configured in base.py, but you can override:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# ========================================
# EMAIL (Console backend for development)
# ========================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ========================================
# INSTALLED APPS (Development tools)
# ========================================
INSTALLED_APPS += [
    'django_extensions',  # Optional: pip install django-extensions
    # 'debug_toolbar',    # Optional: pip install django-debug-toolbar
]

# ========================================
# MIDDLEWARE (Debug toolbar)
# ========================================
# if 'debug_toolbar' in INSTALLED_APPS:
#     MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
#     INTERNAL_IPS = ['127.0.0.1']

# ========================================
# LOGGING (Verbose for development)
# ========================================
LOGGING['loggers']['apps']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'

# ========================================
# SECURITY (Relaxed for development)
# ========================================
# No HTTPS required
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# ========================================
# JAZZMIN (Show UI builder in development)
# ========================================
JAZZMIN_SETTINGS['show_ui_builder'] = True

# ========================================
# DEVELOPMENT-SPECIFIC SETTINGS
# ========================================
# Show full error pages
DEBUG_PROPAGATE_EXCEPTIONS = False

# Don't cache templates
TEMPLATES[0]['OPTIONS']['debug'] = True

print("✅ Development settings loaded")