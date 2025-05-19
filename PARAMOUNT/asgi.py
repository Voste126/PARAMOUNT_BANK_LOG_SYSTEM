"""
ASGI config for PARAMOUNT project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import Dashboard.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PARAMOUNT.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(Dashboard.routing.websocket_urlpatterns),
})
