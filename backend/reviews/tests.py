from datetime import timedelta
import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from unittest.mock import patch
import os 
import redis
from reviews.models import ReviewSession

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def sample_session():
    return ReviewSession.objects.create(
        language="python",
        creator_visitor_id="test-visitor-id"
    )

@pytest.fixture(autouse=True)
def clear_redis():
    """Clear Redis rate limits before every test so they don't interfere."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    r = redis.from_url(redis_url)
    r.flushdb()
    yield
    r.flushdb()

@pytest.fixture(autouse=True)
def bypass_captcha():
    """Mock the Turnstile check so tests don't need a real token."""
    with patch("reviews.views.verify_turnstile", return_value=True):
        yield

# --- Health Check ---

@pytest.mark.django_db
def test_health_check(api_client):
    response = api_client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# --- Session Creation ---

@pytest.mark.django_db
def test_create_session(api_client):
    url = "/api/sessions/"
    response = api_client.post(url, {"language": "django"}, format="json", HTTP_X_VISITOR_ID="test-id")
    assert response.status_code == 201
    assert "token" in response.json()
    assert response.json()["language"] == "django"
    assert ReviewSession.objects.count() == 1

# --- Session Detail ---

@pytest.mark.django_db
def test_get_session_detail(api_client, sample_session):
    url = f"/api/sessions/{sample_session.token}/"
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json()["token"] == sample_session.token

@pytest.mark.django_db
def test_expired_session_returns_410(api_client, sample_session):
    sample_session.expires_at = timezone.now() - timedelta(days=1)
    sample_session.save()
    
    url = f"/api/sessions/{sample_session.token}/"
    response = api_client.get(url)
    assert response.status_code == 410

# --- Review Creation & Validation ---

@pytest.mark.django_db
def test_create_review(api_client, sample_session):
    url = f"/api/sessions/{sample_session.token}/reviews/"
    # Added turnstile_token here
    data = {"code": "print('hello')", "language": "python", "turnstile_token": "dummy"}
    response = api_client.post(url, data, format="json", HTTP_X_VISITOR_ID="test-id")
    
    assert response.status_code == 201
    assert response.json()["status"] == "pending"
    assert response.json()["code"] == "print('hello')"

@pytest.mark.django_db
def test_empty_code_rejected(api_client, sample_session):
    url = f"/api/sessions/{sample_session.token}/reviews/"
    # Added turnstile_token here
    data = {"code": "   ", "language": "python", "turnstile_token": "dummy"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == 400
    assert "code" in response.json()

@pytest.mark.django_db
def test_too_long_code_rejected(api_client, sample_session):
    url = f"/api/sessions/{sample_session.token}/reviews/"
    # Added turnstile_token here
    data = {"code": "a" * 20001, "language": "python", "turnstile_token": "dummy"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == 400
    assert "code" in response.json()

@pytest.mark.django_db
def test_too_many_lines_rejected(api_client, sample_session):
    url = f"/api/sessions/{sample_session.token}/reviews/"
    # Added turnstile_token here
    data = {"code": "a\n" * 301, "language": "python", "turnstile_token": "dummy"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == 400

@pytest.mark.django_db
def test_invalid_language_rejected(api_client, sample_session):
    url = f"/api/sessions/{sample_session.token}/reviews/"
    # Use a language that is NOT in our allowed list
    data = {"code": "print(1)", "language": "cobol", "turnstile_token": "dummy"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == 400
    assert "language" in response.json()