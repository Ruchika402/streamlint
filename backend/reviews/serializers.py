from rest_framework import serializers
from .models import ReviewSession, Review

class ReviewSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewSession
        fields = ["token", "language", "created_at", "expires_at"]

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "code", "language", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

    def validate_code(self, value):
        if not value.strip():
            raise serializers.ValidationError("Code cannot be empty.")
        if len(value) > 20000:
            raise serializers.ValidationError("Code exceeds the 20,000 character limit.")
        if len(value.splitlines()) > 300:
            raise serializers.ValidationError("Code exceeds the 300 line limit.")
        return value

    def validate_language(self, value):
        allowed = ["python", "django", "javascript"]
        if value not in allowed:
            raise serializers.ValidationError(f"Language must be one of: {', '.join(allowed)}")
        return value