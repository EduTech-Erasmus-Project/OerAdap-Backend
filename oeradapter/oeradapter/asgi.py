"""
ASGI config for oeradapter project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os


from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from . import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oeradapter.settings.prod')


# application = get_asgi_application()

# socket connection url
application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": get_asgi_application(),

    # WebSocket
    "websocket": AuthMiddlewareStack(
        URLRouter(
                routing.websocket_urlpatterns
        ),
    ),
})
