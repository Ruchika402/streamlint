import re

# Common patterns for secrets
PATTERNS = [
    (r"(?i)(aws_access_key_id|aws_secret_access_key)\s*=\s*['\"]([^'\"]+)['\"]", r"\1 = '[REDACTED]'"),
    (r"(?i)(password|passwd|pwd|secret|api_key|token)\s*=\s*['\"]([^'\"]+)['\"]", r"\1 = '[REDACTED]'"),
    (r"(AIza[0-9A-Za-z-_]{35})", "[REDACTED_GOOGLE_KEY]"),
    (r"(ghp_[0-9a-zA-Z]{36})", "[REDACTED_GITHUB_TOKEN]"),
]

def redact_secrets(code: str) -> tuple[str, int]:
    """
    Redacts secrets in the code and returns (cleaned_code, count_of_redactions).
    """
    cleaned_code = code
    count = 0
    
    for pattern, replacement in PATTERNS:
        cleaned_code, num_subs = re.subn(pattern, replacement, cleaned_code)
        count += num_subs
        
    return cleaned_code, count