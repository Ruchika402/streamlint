import os

from django.core.asgi import get_asgi_application

# 1. Set environment variable FIRST
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 2. Get ASGI app
django_asgi_app = get_asgi_application()


def create_application():
    # These imports MUST be inside the function to prevent AppRegistryNotReady
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.security.websocket import AllowedHostsOriginValidator

    from config.routing import websocket_urlpatterns

    return ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            URLRouter(
                websocket_urlpatterns
            )
        ),
    })


application = create_application()