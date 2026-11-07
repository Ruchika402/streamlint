# Chaos Testing Report

## Experiment 1: Stop Redis
- **What I did:** Stopped Redis server locally and clicked Review.
- **What I expected:** API returns a friendly 503, frontend doesn't crash.
- **What actually happened:** The frontend failed gracefully and showed the error. The backend did not crash. After restarting Redis, reviews worked normally.
- **Fix applied:** None needed. The `try/except` in `run_review` caught the Redis exception.

## Experiment 2: Paste 5 MB of code
- **What I did:** Attempted to send a 25,000-character payload via curl.
- **What I expected:** 400 Bad Request.
- **What actually happened:** The backend returned `400 Bad Request` with the message `"Code exceeds the 20,000 character limit."`
- **Fix applied:** None needed. Validation in `serializers.py` works.

## Experiment 3: Prompt Injection
- **What I did:** Pasted a comment instructing the AI to ignore previous instructions and output fake JSON.
- **What I expected:** AI ignores the injection.
- **What actually happened:** The AI detected the injection attempt and returned an issue card saying `"Prompt injection attempt detected in comments"`.
- **Fix applied:** None needed. The prompt design in `prompt.py` and output validation in `parser.py` are effective.

## Experiment 5: Concurrent Reviews (Redis Lock)
- **What I did:** Simulated two reviews trying to take the same lock.
- **What I expected:** Only the first succeeds; the second is rejected.
- **What actually happened:** `lock1` was `True`, `lock2` was `None` (rejected). The lock released correctly, and `lock3` was `True`.
- **Fix applied:** None needed. The Redis `SET NX` lock works.

## Experiment 8: Rate Limiting
- **What I did:** Sent 6 rapid requests to the API with the same visitor ID.
- **What I expected:** The 6th request returns `429 Too Many Requests`.
- **What actually happened:** Attempts 1-5 returned `201 Created`. Attempt 6 returned `429` with `"Daily limit reached..."`.
- **Fix applied:** None needed. The rate limiter works as designed.

## Known Limitations
- **Visitor ID Race Condition:** On a fresh share link, the `visitorId` may be empty for a split second. Fixed by adding `&& visitorId` to the `useEffect` dependency check.