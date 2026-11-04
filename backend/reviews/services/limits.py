import os
import redis.asyncio as redis
from datetime import datetime,UTC

def get_redis_client():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.from_url(redis_url, decode_responses=True)

async def check_rate_limit(visitor_id: str, ip_address: str) -> tuple[bool, int, str]:
    """
    Returns (is_allowed, retry_after_seconds, reason).
    Limits: 5 per visitor per day, 15 per IP per day.
    """
    r = get_redis_client()
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    
    vid_key = f"rl:vid:{visitor_id}:{today}"
    ip_key = f"rl:ip:{ip_address}:{today}"
    
    try:
        # Increment counters
        vid_count = await r.incr(vid_key)
        ip_count = await r.incr(ip_key)
        
        # Set expiry to 24 hours if this is the first request today
        if vid_count == 1:
            await r.expire(vid_key, 86400)
        if ip_count == 1:
            await r.expire(ip_key, 86400)
            
        if vid_count > 5:
            return False, 86400, "Daily limit reached for this visitor."
        if ip_count > 15:
            return False, 86400, "Daily limit reached for this IP address."
            
        return True, 0, ""
    finally:
        await r.aclose()

def get_client_ip(request) -> str:
    """
    Safely extracts the client IP, especially behind Render/Vercel proxies.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # Take the first IP in the chain (the actual client)
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "0.0.0.0")