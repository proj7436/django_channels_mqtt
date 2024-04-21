"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.security.websocket import AllowedHostsOriginValidator
import mqtt_app.routing

import django
django.setup()
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        'websocket': AllowedHostsOriginValidator(
            SessionMiddlewareStack(
                URLRouter(mqtt_app.routing.websocket_urlpatterns)
            )
        )
    }
)

