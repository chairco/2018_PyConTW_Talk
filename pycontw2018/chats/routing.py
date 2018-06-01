# chats/routing.py
from django.conf.urls import url

from . import consumers, consumers_sync, consumers_async


websocket_urlpatterns = [
    url(r'^ws/chats/(?P<room_name>[^/]+)/$', consumers_async.ChatConsumer),
    url(r'^ws/chats/sync/(?P<room_name>[^/]+)/$', consumers_sync.ChatConsumer),
]
