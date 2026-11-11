import os
import redis.asyncio as redis
from datetime import datetime, UTC

def get_redis_client():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.from_url(redis_url, decode_responses=True)

async def check_and_increment_budget() -> bool:
    r = get_redis_client()
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    budget_key = f"gemini:calls:{today}"
    
    # Default to 15 calls per day (buffer under the 20 free limit)
    daily_limit = int(os.getenv("DAILY_GEMINI_BUDGET", 15))
    
    try:
        current_calls = await r.get(budget_key)
        current_calls = int(current_calls) if current_calls else 0
        
        if current_calls >= daily_limit:
            return False
            
        # Increment the counter
        await r.incr(budget_key)
        
        # Set expiry to 24 hours on the first call of the day
        if current_calls == 0:
            await r.expire(budget_key, 86400)
            
        return True
    finally:
        await r.aclose()