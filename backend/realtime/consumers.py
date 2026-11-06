from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone
from reviews.models import ReviewSession, Review
import asyncio
import os
import redis.asyncio as redis
from reviews.services.nickname import generate_nickname
from urllib.parse import parse_qs

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

        query_string = self.scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)
        visitor_id = query_params.get("visitor_id", ["unknown"])[0]
        
        nickname = generate_nickname(visitor_id)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "session.event",
                "message": {
                    "type": "presence",
                    "payload": {
                        "count": 1, 
                        "viewers": [{"nickname": nickname, "status": "watching live"}]
                    }
                }
            }
        )


        await self.replay_events()

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
    @database_sync_to_async
    def get_latest_review_id(self):
        latest = Review.objects.filter(session__token=self.token).order_by("-created_at").first()
        return latest.id if latest else None

    async def replay_events(self):
        latest_review_id = await self.get_latest_review_id()
        if not latest_review_id:
            return

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url, decode_responses=True)
        
        try:
            list_key = f"events:{latest_review_id}"
            past_events = await r.lrange(list_key, 0, -1)
            for event_json in past_events:
                # We send the raw JSON string directly to the socket
                await self.send(text_data=event_json)
        finally:
            await r.aclose()

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