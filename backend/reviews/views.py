from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import ReviewSession
from .serializers import ReviewSessionSerializer, ReviewSerializer

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

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            visitor_id = request.headers.get("X-Visitor-Id", "unknown")
            
            # Save the review (code_hash will be calculated in the pipeline later)
            review = serializer.save(
                session=session,
                visitor_id=visitor_id,
                code_hash="temp_hash_for_now" 
            )
            return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.http import HttpResponse
import os
from django.conf import settings

def ws_test_page(request):
    file_path = os.path.join(settings.BASE_DIR, 'ws_test.html')
    with open(file_path, 'r') as f:
        return HttpResponse(f.read(), content_type="text/html")
