import os
from django.core.asgi import get_asgi_application

# 1. Setup Django settings and get ASGI app FIRST
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django_asgi_app = get_asgi_application()

# 2. Import routing and middleware (after Django is ready)
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402
from config.routing import websocket_urlpatterns  # noqa: E402

# 3. Route HTTP and WebSockets
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})