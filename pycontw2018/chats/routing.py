# chats/routing.py
from django.conf.urls import url

from . import consumers


websocket_urlpatterns = [
    url(r'^ws/chats/(?P<room_name>[^/]+)/$', consumers.ChatConsumer),
]
