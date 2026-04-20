"""Admin analytics URL patterns."""

from django.urls import include, path

urlpatterns = [
    path("analytics/", include("analytics.urls")),
]
