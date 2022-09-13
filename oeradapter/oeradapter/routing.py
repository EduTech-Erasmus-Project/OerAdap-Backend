from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
    url(r'^ws/adapter/video/progress/(?P<pk>[^/]+)$', consumers.VideoConsumer.as_asgi()),
]