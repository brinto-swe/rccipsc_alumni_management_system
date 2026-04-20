"""Profession URL patterns."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from professions.views import ProfessionViewSet


router = DefaultRouter()
router.register("", ProfessionViewSet, basename="profession")

urlpatterns = [
    path("", include(router.urls)),
]
