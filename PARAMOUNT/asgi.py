"""
ASGI config for PARAMOUNT project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PARAMOUNT.settings')

# Debugging to confirm DJANGO_SETTINGS_MODULE is set correctly
print("DJANGO_SETTINGS_MODULE:", os.environ.get('DJANGO_SETTINGS_MODULE'))

# Initialize Django ASGI application early to ensure apps are loaded
http_application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": http_application,  # Use the initialized Django ASGI application for HTTP
})
