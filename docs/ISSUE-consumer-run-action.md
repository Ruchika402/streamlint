# 🐛 Bug: WebSocket Consumer Silently Drops `"run"` Action

## 📝 Description
When a user sends the `"run"` command over the live WebSocket connection, the server receives the connection but completely ignores the payload. It does not trigger the AI pipeline, it does not send a `running` status back to the browser, and it outputs zero error logs to Render.

## 🖥️ Environment
- **Local:** WSL2 (Ubuntu), Python 3.12, Django 5.0.6, Daphne 4.1.2, Channels 4.1.0
- **Live Host:** Render (Free tier)
- **Database:** Neon (Postgres)
- **Redis:** Upstash (Redis)
- **AI Model:** `gemini-3.5-flash-lite`

## 🛠️ Steps to Reproduce
1. Deploy the current `main` branch to Render.
2. Create a session: `curl -X POST https://streamlint-backend.onrender.com/api/sessions/ -H "Content-Type: application/json" -d '{"language": "python"}'`
3. Create a review: `curl -X POST https://streamlint-backend.onrender.com/api/sessions/{token}/reviews/ -H "Content-Type: application/json" -d '{"code": "import os\nprint(1)", "language": "python"}'`
4. Open `https://streamlint-backend.onrender.com/ws_test.html` in Chrome.
5. Paste the token and click **Connect** (Browser shows `Connected!`).
6. Open Chrome DevTools (F12) Console and send:
   `ws.send(JSON.stringify({ action: "run", review_id: <ID> }))`
7. Chrome returns `undefined` (message sent successfully).

## 🚨 Current Behavior
- **Browser:** The connection stays open, but no status message or AI stream is received. 
- **Render Logs:** Completely empty. There are no `print()` statements, no `🚨 LIVE SERVER RECEIVED RUN COMMAND` output, and no error tracebacks.
- **Local Server:** Same behavior—the server's `receive_json` seemingly never fires.

## ✅ Expected Behavior
1. The server logs `🚨 LIVE SERVER RECEIVED RUN COMMAND FOR REVIEW: <ID>`.
2. The browser immediately receives `{"type": "status", "payload": {"state": "running"}}`.
3. `run_review()` executes, broadcasting `static_findings` and `issue` events to the WebSocket group.
4. Late joiners receive a replay from the Redis list.

## 🕵️ Root Cause Hypothesis
The WebSocket connection is established (TLS handshake, token validation, and group join are all successful), but the `receive_json` handler is not being invoked. Possible causes:
1. **Silent drop at the ASGI layer:** Daphne receives the text frame but the Channels dispatcher does not route it to the consumer's `receive_json`.
2. **Client-side dispatch bug:** The `ws_test.html` file may be connecting to a different URL than intended (e.g., cached file still pointing at `wss://...onrender.com` instead of `ws://127.0.0.1:8000`).
3. **Server-side exception swallowed:** An exception occurs before the `print()` flush, so nothing reaches stdout.

## 🔧 Proposed Fix Plan
1. **Add a bare `print("receive_json hit")` at the very top of `receive_json`** to confirm routing.
2. **Log every frame:** Wrap `receive_json` in a `try/except` and print `content` (truncated) to verify if the frame arrives.
3. **Bypass the browser:** Use `WebsocketCommunicator` in `manage.py shell` against the live ASGI app to prove the consumer is the problem (not the browser).
4. **Verify `routing.py`:** Ensure the URL pattern matches the exact token (no trailing slash) and that the consumer class is imported correctly.
5. **Once confirmed:** Switch to `asyncio.create_task(run_review(...))` for non-blocking execution.

## 🚫 What is NOT the issue
- ❌ Redis connection (the WebSocket joins the group successfully)
- ❌ Token validation (the session exists and connects)
- ❌ Gemini API key (the pipeline ran fine locally when called directly)
- ❌ Model name (verified with `generate_content` in the shell)