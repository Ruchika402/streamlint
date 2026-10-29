import secrets
from datetime import timedelta
from django.db import models
from django.utils import timezone

class ReviewSession(models.Model):
    token = models.CharField(max_length=32, unique=True, db_index=True)
    language = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    creator_visitor_id = models.CharField(max_length=36)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(16)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Session {self.token} ({self.language})"


class Review(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("done", "Done"),
        ("failed", "Failed"),
    ]

    session = models.ForeignKey(ReviewSession, on_delete=models.CASCADE, related_name="reviews")
    visitor_id = models.CharField(max_length=36)
    code = models.TextField()
    code_hash = models.CharField(max_length=64, db_index=True)
    language = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    issues = models.JSONField(default=list, blank=True)
    summary = models.TextField(blank=True, null=True)
    error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Review {self.id} for Session {self.session.token} ({self.status})"
