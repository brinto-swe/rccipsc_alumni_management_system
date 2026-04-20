"""Directory URL patterns."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from directory.views import AlumniDirectoryViewSet


router = DefaultRouter()
router.register("alumni", AlumniDirectoryViewSet, basename="directory-alumni")

urlpatterns = [
    path("", include(router.urls)),
]
