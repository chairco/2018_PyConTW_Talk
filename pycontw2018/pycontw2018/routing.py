# pycontw2018/routing.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import chats.routing


application = ProtocolTypeRouter({
    # Empty for now(http->django views added by default)
    # (http -> django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chats.routing.websocket_urlpatterns
        )
    ),
})
