from django.urls import re_path
from realtime.consumers import SessionConsumer, HealthConsumer

websocket_urlpatterns = [
    re_path(r"^ws/sessions/(?P<token>[^/]+)/$", SessionConsumer.as_asgi()),
    re_path(r"^ws/health/$", HealthConsumer.as_asgi()),
]