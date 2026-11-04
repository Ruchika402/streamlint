import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .services.limits import check_rate_limit, get_client_ip
from .services.captcha import verify_turnstile

from .models import ReviewSession
from .serializers import ReviewSerializer, ReviewSessionSerializer


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"status": "ok"})

class SessionCreateView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # No login required

    def post(self, request):
        language = request.data.get("language", "python")
        visitor_id = request.headers.get("X-Visitor-Id", "unknown")
        
        session = ReviewSession.objects.create(
            language=language,
            creator_visitor_id=visitor_id
        )
        return Response(ReviewSessionSerializer(session).data, status=status.HTTP_201_CREATED)

class SessionDetailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, token):
        session = get_object_or_404(ReviewSession, token=token)
        if session.expires_at < timezone.now():
            return Response({"error": "Session expired"}, status=status.HTTP_410_GONE)
            
        reviews = session.reviews.all().order_by("-created_at")
        data = ReviewSessionSerializer(session).data
        data["reviews"] = ReviewSerializer(reviews, many=True).data
        return Response(data)

class ReviewCreateView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, token):
        session = get_object_or_404(ReviewSession, token=token)
        if session.expires_at < timezone.now():
            return Response({"error": "Session expired"}, status=status.HTTP_410_GONE)

        visitor_id = request.headers.get("X-Visitor-Id", "unknown")
        ip_address = get_client_ip(request)

        # Check limits synchronously for DRF
        import asyncio
        is_allowed, retry_after, reason = asyncio.run(check_rate_limit(visitor_id, ip_address))
        
        if not is_allowed:
            return Response(
                {"error": reason, "retry_after": retry_after}, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # --- START CAPTCHA CHECK ---
        turnstile_token = request.data.get("turnstile_token")
        if not turnstile_token:
            return Response({"error": "CAPTCHA token missing"}, status=status.HTTP_400_BAD_REQUEST)

        captcha_ok = asyncio.run(verify_turnstile(turnstile_token, ip_address))
        if not captcha_ok:
            return Response({"error": "CAPTCHA verification failed"}, status=status.HTTP_400_BAD_REQUEST)
        # --- END CAPTCHA CHECK ---

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(
                session=session,
                visitor_id=visitor_id,
                code_hash="temp_hash_for_now" 
            )
            return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def ws_test_page(request):
    file_path = os.path.join(settings.BASE_DIR, 'ws_test.html')
    with open(file_path, 'r') as f:
        return HttpResponse(f.read(), content_type="text/html")



