"""Notification URL patterns."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from notifications.views import NotificationPreferenceViewSet, NotificationViewSet


router = DefaultRouter()
router.register("", NotificationViewSet, basename="notification")
router.register("preferences", NotificationPreferenceViewSet, basename="notification-preference")

urlpatterns = [
    path("", include(router.urls)),
]
