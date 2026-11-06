
# Real-Time AI Code Reviewer

Paste Python, Django, or JavaScript code. Get Ruff findings in under a second,
then Gemini's AI review streamed issue-by-issue, pinned to line numbers.
Every browser on the same session link sees the same live stream.

<p align="center">
  <img src="frontend/public/streamlint-demo.png" alt="Streamlint Demo" width="600" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(166,30,77,0.15);" />
</p>

**Status:** 🚧 In development 

---


## Stack

- **Backend:** Django + Channels (ASGI), Redis (Upstash), Postgres (Neon), Gemini API (free tier)
- **Frontend:** React + TypeScript (Vite), CodeMirror 6
- **Hosting:** Render (Backend), Vercel (Frontend)
- **CI:** GitHub Actions

## Live Backend

Check if the server is awake: [Health Check](https://streamlint-backend.onrender.com/health/)

## Local setup

(TBD — will fill in as we build)

## License

MIT
