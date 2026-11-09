import asyncio
import websockets
import json
import time
import httpx
import statistics

BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000"

async def create_session_and_review():
    async with httpx.AsyncClient() as client:
        # 1. Create Session
        res = await client.post(f"{BASE_URL}/api/sessions/", json={"language": "python"})
        token = res.json()["token"]
        
        # 2. Create Review
        code = "import os\n\ndef divide(a, b):\n    return a / b\n\nprint(divide(10, 0))"
        review_res = await client.post(
            f"{BASE_URL}/api/sessions/{token}/reviews/",
            json={"code": code, "language": "python", "turnstile_token": "dummy"},
            headers={"X-Visitor-Id": "load-test-user"}
        )
        review_id = review_res.json()["id"]
        
        return token, review_id

async def viewer(token, viewer_id, results, start_event):
    uri = f"{WS_URL}/ws/sessions/{token}/?visitor_id={viewer_id}"
    async with websockets.connect(uri, additional_headers={"Origin": "http://localhost:8000"}) as ws:
        await start_event.wait() # Wait for all viewers to connect
        
        first_issue_time = None
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=15)
                data = json.loads(msg)
                
                if data["type"] == "issue" and first_issue_time is None:
                    first_issue_time = time.time()
                    results.append(first_issue_time)
                    
                if data["type"] == "status" and data["payload"]["state"] == "done":
                    break
            except asyncio.TimeoutError:
                break

async def run_load_test():
    print("Creating session and review...")
    token, review_id = await create_session_and_review()
    
    num_viewers = 50
    print(f"Starting {num_viewers} viewers...")
    
    start_event = asyncio.Event()
    results = []
    
    # 1. Connect 50 viewers
    tasks = [asyncio.create_task(viewer(token, f"viewer-{i}", results, start_event)) for i in range(num_viewers)]
    
    # Wait a moment for all WebSockets to connect
    await asyncio.sleep(2)
    
    print("All viewers connected. Triggering review...")
    start_time = time.time()
    start_event.set()
    
    # 2. Trigger the review via WebSocket (simulating the creator)
    creator_uri = f"{WS_URL}/ws/sessions/{token}/?visitor_id=creator"
    async with websockets.connect(creator_uri, additional_headers={"Origin": "http://localhost:8000"}) as ws:
        await ws.send(json.dumps({"action": "run", "review_id": review_id}))
        
        # Wait for the review to finish
        await asyncio.gather(*tasks)
    
    end_time = time.time()
    
    # 3. Calculate Metrics
    print("\n--- LOAD TEST RESULTS ---")
    print(f"Total time: {end_time - start_time:.2f} seconds")
    print(f"Viewers: {num_viewers}")
    
    if results:
        latencies = [(t - start_time) * 1000 for t in results] # Convert to ms
        p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else max(latencies)
        print(f"Time to first issue (average): {statistics.mean(latencies):.2f} ms")
        print(f"Time to first issue (p95): {p95:.2f} ms")
    else:
        print("No issues were received.")

if __name__ == "__main__":
    asyncio.run(run_load_test())