import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
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
    data = {"code": "print('hello')", "language": "python"}
    response = api_client.post(url, data, format="json", HTTP_X_VISITOR_ID="test-id")
    
    assert response.status_code == 201
    assert response.json()["status"] == "pending"
    assert response.json()["code"] == "print('hello')"

@pytest.mark.django_db
def test_empty_code_rejected(api_client, sample_session):
    url = f"/api/sessions/{sample_session.token}/reviews/"
    data = {"code": "   ", "language": "python"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == 400
    assert "code" in response.json()

@pytest.mark.django_db
def test_too_long_code_rejected(api_client, sample_session):
    url = f"/api/sessions/{sample_session.token}/reviews/"
    data = {"code": "a" * 20001, "language": "python"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == 400
    assert "code" in response.json()

@pytest.mark.django_db
def test_too_many_lines_rejected(api_client, sample_session):
    url = f"/api/sessions/{sample_session.token}/reviews/"
    data = {"code": "a\n" * 301, "language": "python"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == 400

@pytest.mark.django_db
def test_invalid_language_rejected(api_client, sample_session):
    url = f"/api/sessions/{sample_session.token}/reviews/"
    data = {"code": "print(1)", "language": "ruby"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == 400
    assert "language" in response.json()