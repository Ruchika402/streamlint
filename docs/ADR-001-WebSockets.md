# ADR 001: WebSockets over SSE

## Context
We need to stream AI issues to multiple viewers in real-time. We could use Server-Sent Events (SSE) or WebSockets.

## Decision
We chose WebSockets because we need bi-directional communication (the client sends the "run" command, the server streams issues). SSE is only one-way.

## Consequences
- **Pros:** Real-time bi-directional, supports presence tracking, works with Django Channels.
- **Cons:** Slightly more complex to set up than SSE.