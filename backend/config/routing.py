from django.urls import re_path
from realtime.consumers import SessionConsumer

websocket_urlpatterns = [
    re_path(r"^ws/sessions/(?P<token>[^/]+)/$", SessionConsumer.as_asgi()),
]