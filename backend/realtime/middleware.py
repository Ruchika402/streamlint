from urllib.parse import urlparse
from channels.security.websocket import OriginValidator
from django.conf import settings

class CustomOriginValidator(OriginValidator):
    """
    A custom validator that uses the CORS_ALLOWED_ORIGINS setting.
    If a request comes from a `file://` URL (like local testing), it's allowed.
    """
    def __init__(self, application):
        super().__init__(application, allowed_origins=settings.CORS_ALLOWED_ORIGINS)

    def valid_origin(self, parsed_origin):
        # Always allow local file testing (origin is 'null')
        if parsed_origin is None:
            return True
        return super().valid_origin(parsed_origin)