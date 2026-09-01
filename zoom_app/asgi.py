import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import re_path

from rooms.consumers import SignalingConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zoom_app.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        re_path(r"ws/room/(?P<room_code>[^/]+)/$", SignalingConsumer.as_asgi()),
                    ]
                )
            )
        ),
    }
)
