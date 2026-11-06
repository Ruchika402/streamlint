import asyncio
import logging
import os
import json
import redis.asyncio as redis
from django.utils import timezone
from google import genai
from google.genai import types


from reviews.models import Review
from reviews.services.static import run_ruff
from reviews.services.prompt import build_prompt
from reviews.services.parser import parse_stream_chunk
from realtime.events import issue_event, status_event

logger = logging.getLogger(__name__)

async def run_review(review_id: int, token: str):
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    r = redis.from_url(redis_url, decode_responses=True)
    lock_key = f"lock:{token}"
    group_name = f"session_{token}"

    

    # 1. Take the Redis lock
    lock_acquired = await r.set(lock_key, "locked", nx=True, ex=120)
    if not lock_acquired:
        await r.aclose()
        return

    try:
        # 2. Update DB status
        review = await Review.objects.aget(id=review_id)
        review.status = "running"
        await review.asave()

        seq = 1
        await broadcast(group_name, status_event(review_id, "running", seq))
        seq += 1

        # 3. Run Ruff
        code = review.code
        language = review.language
        ruff_findings = run_ruff(code, language)
        
        static_event = {
            "type": "static_findings",
            "review_id": review_id,
            "seq": seq,
            "payload": {"findings": ruff_findings}
        }
        await broadcast(group_name, static_event)
        seq += 1

        # 4. Stream Gemini
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
        
        client = genai.Client(api_key=api_key)
        prompt = build_prompt(code, language, ruff_findings)
        
        buffer = ""
        all_issues = []
        summary_data = None

        async def stream_gemini():
            nonlocal buffer, seq, summary_data
            response = await client.aio.models.generate_content_stream(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=2000,
                )
            )
            
            async for chunk in response:
                if chunk.text:
                    parsed, buffer = parse_stream_chunk(chunk.text, buffer)
                    for item in parsed:
                        if item["type"] == "issue":
                            all_issues.append(item["data"])
                            event = issue_event(
                                review_id,
                                line=item["data"].get("line", 0),
                                severity=item["data"].get("severity", "info"),
                                category=item["data"].get("category", "style"),
                                message=item["data"].get("message", ""),
                                suggestion=item["data"].get("suggestion", ""),
                                seq=seq
                            )
                            await broadcast(group_name, event)
                            seq += 1
                        elif item["type"] == "summary":
                            summary_data = item["data"]

        # Run the stream with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await asyncio.wait_for(stream_gemini(), timeout=120.0)
                break
            except asyncio.TimeoutError:
                logger.error("Gemini stream timed out.")
                if attempt == max_retries - 1:
                    raise Exception("AI review timed out.")
            except Exception as e:
                if "503" in str(e) and attempt < max_retries - 1:
                    logger.warning("Gemini busy (503). Retrying in 3 seconds...")
                    await asyncio.sleep(3)
                else:
                    raise e

        # 5. FLUSH THE BUFFER (The crucial fix!)
        if buffer.strip():
            parsed, _ = parse_stream_chunk("\n", buffer)
            for item in parsed:
                if item["type"] == "issue":
                    all_issues.append(item["data"])
                    event = issue_event(
                        review_id,
                        line=item["data"].get("line", 0),
                        severity=item["data"].get("severity", "info"),
                        category=item["data"].get("category", "style"),
                        message=item["data"].get("message", ""),
                        suggestion=item["data"].get("suggestion", ""),
                        seq=seq
                    )
                    await broadcast(group_name, event)
                    seq += 1
                elif item["type"] == "summary":
                    summary_data = item["data"]

        # 6. Save to Postgres
        review.issues = all_issues
        review.summary = str(summary_data) if summary_data else "Review complete."
        review.status = "done"
        review.finished_at = timezone.now()
        await review.asave()

        summary_event = {
            "type": "summary",
            "review_id": review_id,
            "seq": seq,
            "payload": summary_data or {"summary": "Done"}
        }
        await broadcast(group_name, summary_event)
        seq += 1

        await broadcast(group_name, status_event(review_id, "done", seq))

    except Exception as e:
        logger.exception(f"Pipeline error: {e}")
        try:
            review = await Review.objects.aget(id=review_id)
            review.status = "failed"
            review.error = str(e)
            await review.asave()
        except Exception:
            pass
        
        await broadcast(group_name, {
            "type": "error",
            "review_id": review_id,
            "seq": 99,
            "payload": {"message": str(e)}
        })
        
    finally:
        await r.delete(lock_key)
        await r.aclose()

async def broadcast(group_name: str, event: dict):
    """Send to WebSocket and save to Redis list."""
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    
    await channel_layer.group_send(group_name, {"type": "session.event", "message": event})
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    r = redis.from_url(redis_url, decode_responses=True)
    list_key = f"events:{event.get('review_id', 0)}"
    
    await r.rpush(list_key, json.dumps(event))
    await r.expire(list_key, 86400)
    await r.aclose()