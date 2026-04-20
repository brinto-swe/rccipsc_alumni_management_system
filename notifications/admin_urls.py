"""Admin notification URLs."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from notifications.views import AdminBroadcastAPIView, EmailQueueViewSet


router = DefaultRouter()
router.register("email-queue", EmailQueueViewSet, basename="email-queue")

urlpatterns = [
    path("", include(router.urls)),
    path("broadcasts/", AdminBroadcastAPIView.as_view(), name="admin-broadcasts"),
]
