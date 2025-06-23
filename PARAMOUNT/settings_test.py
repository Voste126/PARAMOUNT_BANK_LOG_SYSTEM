"""
Test settings for PARAMOUNT project.
This file is used specifically for running tests to avoid database connection issues.
"""

from .settings import *
import tempfile

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Use in-memory SQLite database for faster tests
    }
}

# Disable migrations for faster test runs
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Use console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable Redis for testing
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# Speed up password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING_CONFIG = None

# Test-specific settings
DEBUG = True
SECRET_KEY = 'test-secret-key-for-testing-only'

# Override email domain for testing
STAFF_EMAIL_DOMAIN = '@paramount.co.ke'
IT_SUPPORT_EMAIL = 'it-support@test.com'
