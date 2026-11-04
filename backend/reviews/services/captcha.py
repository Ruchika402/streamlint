import os
import httpx

async def verify_turnstile(token: str, ip_address: str) -> bool:
    """
    Verifies the Turnstile token with Cloudflare.
    """
    secret = os.getenv("TURNSTILE_SECRET")
    if not secret:
        return True # If no secret is set (local dev), skip verification

    url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    data = {
        "secret": secret,
        "response": token,
        "remoteip": ip_address
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)
        result = response.json()
        return result.get("success", False)