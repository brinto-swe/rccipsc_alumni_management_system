"""Admin feed moderation URLs."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from posts.views import AdminReportViewSet


router = DefaultRouter()
router.register("reports", AdminReportViewSet, basename="admin-report")

urlpatterns = [
    path("", include(router.urls)),
]
