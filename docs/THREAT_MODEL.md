# Threat Model

## Assets
- **Gemini API Quota:** 20 requests per day.
- **User Code:** Pasted code may contain secrets.
- **Availability:** The app must not crash under load.

## Threats and Mitigations
1. **Quota Burning:** A bot spams the "Review" button.
   - *Mitigation:* Cloudflare Turnstile, rate limits (5/day/visitor), and a daily budget breaker.
2. **Secret Leakage:** A user pastes an AWS key.
   - *Mitigation:* Regex-based secret redaction before sending to Gemini.
3. **Prompt Injection:** A user pastes code containing instructions to ignore previous prompts.
   - *Mitigation:* The code is delimited and treated as data. We validate output line-by-line.