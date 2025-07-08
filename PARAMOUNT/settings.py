"""
Django settings for PARAMOUNT project.

This file contains all configuration for the Django project, including security, database, installed apps, middleware, static files, email, authentication, REST framework, channels, CORS, and security settings.

Sections:
- Path and environment setup: Sets up base directory and loads environment variables from .env.
- Security: Secret key, debug mode, allowed hosts.
- Application definition: Installed apps and middleware.
- Templates: Template engine configuration.
- WSGI/ASGI: Entry points for WSGI and ASGI servers.
- Database: PostgreSQL configuration using environment variables.
- Password validation: Enforces password strength and security.
- Internationalization: Language and timezone settings.
- Static files: Static file storage and serving configuration.
- Email: SMTP settings for sending OTPs and notifications.
- Custom project settings: Staff email domain, IT support email, website link.
- REST Framework: JWT authentication and default permissions.
- JWT: Token lifetimes and claims for authentication.
- Custom user model: Uses Staff.Staff as the user model.
- Channels: WebSocket and async support using Redis.
- Swagger: API documentation settings.
- CORS: Cross-origin resource sharing for frontend integration.
- Security: Additional HTTP and cookie security settings.

For more information, see the Django documentation:
https://docs.djangoproject.com/en/5.1/topics/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY =  'django-insecure-^i@r324!^c9q2k7($vdx!)^zu+^+wj43$ljylj7=9c#f5we@1o'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() in ['true', '1']

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #installed apps
    'rest_framework',
    'django_prometheus',
    'drf_yasg',
    'corsheaders',
    'rest_framework_simplejwt.token_blacklist',
    
    'Staff',
    'ReportLog',
    'channels',
    
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'PARAMOUNT.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Add this line to include the templates directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'PARAMOUNT.wsgi.application'
ASGI_APPLICATION = 'PARAMOUNT.asgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Email settings for OTP
# DEFAULT_FROM_EMAIL = 'noreply@paramount.com'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For development/testing
# For production, configure SMTP backend and credentials securely
# EMAIL_HOST = 'smtp.yourprovider.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'youruser'
# EMAIL_HOST_PASSWORD = 'yourpassword'
# EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = 'noreply@paramount.com'
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.yourprovider.com')
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'youruser')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'yourpassword')
EMAIL_USE_TLS = True

STAFF_EMAIL_DOMAIN = os.getenv('STAFF_EMAIL_DOMAIN', '@paramount.co.ke')
IT_SUPPORT_EMAIL = os.getenv('IT_SUPPORT_EMAIL', 'steveaustine126@gmail.com')

# Add the website link for onboarding emails
WEBSITE_LINK = os.getenv('WEBSITE_LINK', 'https://www.paramountbank.com')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Updated to 15 minutes for better usability
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # Updated to 7 days for extended session
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

AUTH_USER_MODEL = 'Staff.Staff'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [("127.0.0.1", 6379)]},
    },
}

SWAGGER_USE_COMPAT_RENDERERS = False

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Replace with your frontend's URL
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://localhost:8080",  # Local network access
    "http://192.168.8.101:8080",  # Network access
    "http://172.20.0.1:8080",  # Network access
]


# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', 'False').lower() in ['true', '1']
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
