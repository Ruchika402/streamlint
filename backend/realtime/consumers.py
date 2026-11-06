from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone
from reviews.models import ReviewSession
import asyncio

class SessionConsumer(AsyncJsonWebsocketConsumer):
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
    async def receive_json(self, content, **kwargs):
        action = content.get("action")
        if action not in ["ping", "run"]:
            return  
        
        if action == "ping":
            await self.send_json({"type": "pong"})
            
        elif action == "run":
            review_id = content.get("review_id")
            print(f"🚨 RECEIVED RUN COMMAND FOR REVIEW: {review_id}", flush=True)
            
            if review_id:
                await self.send_json({
                    "type": "status",
                    "payload": {"state": "running"}
                })
                from reviews.services.pipeline import run_review
                # Keep a reference so the task isn't garbage-collected
                self._task = asyncio.create_task(run_review(review_id, self.token))

    async def session_event(self, event):
        await self.send_json(event["message"])