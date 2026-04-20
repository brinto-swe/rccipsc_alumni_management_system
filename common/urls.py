"""Shared URL patterns."""

from django.urls import path

from common.views import HealthCheckAPIView


urlpatterns = [
    path("", HealthCheckAPIView.as_view(), name="health-check"),
]
