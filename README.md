
# Real-Time AI Code Reviewer

Paste Python, Django, or JavaScript code. Get Ruff findings in under a second,
then Gemini's AI review streamed issue-by-issue, pinned to line numbers.
Every browser on the same session link sees the same live stream.

**Status:** 🚧 In development (Phase 0)

---

## Event contract

Every WebSocket message is JSON with a `type`, `review_id`, and `seq` (sequence number).

| type | payload | sent when |
|---|---|---|
| `status` | `state`: `queued`, `running`, `cached`, `done`, `failed` | state changes |
| `redaction` | `count` — number of secrets masked | before the review |
| `static_findings` | list of Ruff findings (`line`, `code`, `message`) | after Ruff runs |
| `issue` | `line`, `severity`, `category`, `message`, `suggestion` | per parsed Gemini line |
| `summary` | `text`, counts per severity | end of review |
| `error` | `code`, friendly `message` | any failure |
| `presence` | `viewers` — count | someone joins or leaves |

Backend and frontend both obey this contract.

---

## Stack

- **Backend:** Django + Channels (ASGI), Redis (Upstash), Postgres (Neon), Gemini API (free tier)
- **Frontend:** React + TypeScript (Vite), CodeMirror 6
- **Hosting:** Vercel . Fallback: Render.
- **CI:** GitHub Actions

## Local setup

(TBD — will fill in as we build)

## License

MIT
