from reviews.services.redact import redact_secrets


def test_redact_aws_key():
    code = "aws_access_key_id = 'AKIAIOSFODNN7EXAMPLE'"
    cleaned, count = redact_secrets(code)
    assert count == 1
    assert cleaned == "aws_access_key_id = '[REDACTED]'"


def test_redact_password():
    code = "password = 'supersecret123'"
    cleaned, count = redact_secrets(code)
    assert count == 1
    assert cleaned == "password = '[REDACTED]'"


def test_redact_multiple_secrets():
    code = """
aws_access_key_id = 'AKIAIOSFODNN7EXAMPLE'
password = 'supersecret123'
github_token = 'ghp_1234567890abcdefghijklmnopqrstuvwxyz'
"""
    cleaned, count = redact_secrets(code)
    assert count == 3
    assert "[REDACTED]" in cleaned
    assert "AKIAIOSFODNN7EXAMPLE" not in cleaned


def test_redact_no_secrets():
    code = "print('hello world')"
    cleaned, count = redact_secrets(code)
    assert count == 0
    assert cleaned == code