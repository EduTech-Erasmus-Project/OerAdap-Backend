"""
ASGI config for oeradapter project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter
from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path

from . import consumers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oeradapter.settings')

# application = get_asgi_application()

# socket connection url
application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": get_asgi_application(),

    # WebSocket
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                # url(r"^api/adapter/(?P<tag>[\w.@+-]+)/$", VideoConsumer),
                #url(r"^api/adapter/video/progress/(?P<tag>[\w.@+-]+)/$", consumers.VideoConsumer.as_asgi()),
                path("api/adapter/video/progress/<int:pk>", consumers.VideoConsumer.as_asgi())
            ]
        ),
    ),
})
