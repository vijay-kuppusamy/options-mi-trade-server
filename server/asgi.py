import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from base.authenticate import ChannelJwtAuthMiddleWare
from django.core.asgi import get_asgi_application

import base.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django_asgi_app = get_asgi_application()
django.setup()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket': ChannelJwtAuthMiddleWare(
        URLRouter(
            base.routing.websocket_urlpatterns
        )
    )
})
    