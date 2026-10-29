from django.contrib import admin
from django.urls import path
from reviews.views import HealthCheckView, SessionCreateView, SessionDetailView, ReviewCreateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", HealthCheckView.as_view(), name="health"),
    path("api/sessions/", SessionCreateView.as_view(), name="session-create"),
    path("api/sessions/<str:token>/", SessionDetailView.as_view(), name="session-detail"),
    path("api/sessions/<str:token>/reviews/", ReviewCreateView.as_view(), name="review-create"),
]