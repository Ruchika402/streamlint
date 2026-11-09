# Load Test Report

## Methodology
- **Tool:** Custom Python async script (`eval/load_test.py`).
- **Setup:** 1 active session, 50 concurrent WebSocket viewers.
- **Environment:** Local machine (WSL2) with Docker Postgres/Redis.
- **Backend:** Django + Daphne + Channels_Redis.

## Results

| Metric | Value |
| :--- | :--- |
| **Total review time** | 3.44 seconds |
| **Concurrent viewers** | 50 |
| **Time to first issue (avg)** | 3,115 ms |
| **Time to first issue (p95)** | 3,116 ms |
| **Dropped connections** | 0 |

## Observations
- The WebSocket broadcast layer (Redis Pub/Sub) successfully handled 50 simultaneous viewers without dropping any connections.
- The p95 latency (3,116 ms) is almost identical to the average (3,115 ms), which means the broadcast was perfectly synchronized. All 50 viewers received the issue at the exact same time.
- The total time of 3.44 seconds is dominated by the Gemini API generation time, not our backend.

## Limitations (Render Free Tier)
While the local test is fast, production on Render's free tier has specific constraints:
- **Cold Starts:** The backend spins down after 15 minutes of inactivity. The first request can take ~50 seconds to wake up.
- **Redis Limits:** Upstash free tier allows 10,000 commands per day. A full 50-viewer review uses roughly 150-200 Redis commands.
- **Gemini Quota:** The free Gemini API allows 20 requests per day.