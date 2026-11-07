# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-11-07

### Added
- Real-time AI code reviews streaming line-by-line via WebSockets.
- Support for 15 languages (Python, Django, JavaScript, Java, C, C++, C#, Go, Rust, Ruby, PHP, HTML, Swift, R, SQL).
- Shareable session links with live viewer presence and replay for late joiners.
- Cloudflare Turnstile integration to prevent bot abuse.
- Rate limiting (5/day per visitor, 20/day per IP) and a daily Gemini budget breaker.
- Secret redaction (AWS keys, GitHub tokens, etc.) before code is sent to the AI.
- React frontend with CodeMirror 6, line annotations, and a beautiful pink design.
- Docker setup for one-command local development (`docker compose up --build`).
- CI/CD pipeline with GitHub Actions (backend, frontend, and Docker builds).
- SEO pages for all 15 languages to drive organic search traffic.

### Fixed
- WebSocket connection issues with Upstash Redis (SSL context).
- Race condition where the visitor ID was empty on shared link loads.
- Mobile responsiveness for the editor toolbar and header.