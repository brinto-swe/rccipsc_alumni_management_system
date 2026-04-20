"""Admin-only event URL patterns."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from events.views import AdminEventViewSet


router = DefaultRouter()
router.register("events", AdminEventViewSet, basename="admin-event")

urlpatterns = [
    path("", include(router.urls)),
]
