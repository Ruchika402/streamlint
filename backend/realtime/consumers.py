import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from reviews.models import ReviewSession

class SessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.token = self.scope["url_route"]["kwargs"]["token"]
        self.group_name = f"session_{self.token}"

        # 1. Validate token exists and isn't expired BEFORE accepting
        is_valid = await self.check_session_valid()
        if not is_valid:
            # 4404 = Not Found / Invalid token
            await self.close(code=4404)
            return

        # 2. Join the group and accept the connection
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    @database_sync_to_async
    def check_session_valid(self):
        try:
            session = ReviewSession.objects.get(token=self.token)
            if session.expires_at < timezone.now():
                return False
            return True
        except ReviewSession.DoesNotExist:
            return False

    # Security: Only allow whitelisted actions from the client
    async def receive_json(self, content):
        action = content.get("action")
        if action not in ["ping", "run"]:
            return  # Ignore any attempt to inject fake events
        
        if action == "ping":
            await self.send(text_data=json.dumps({"type": "pong"}))

    # Forward messages from the group to the WebSocket
    async def session_event(self, event):
        await self.send(text_data=json.dumps(event["message"]))