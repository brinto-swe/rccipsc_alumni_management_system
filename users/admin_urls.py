"""Admin user-management URLs."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import AdminUserViewSet


router = DefaultRouter()
router.register("users", AdminUserViewSet, basename="admin-user")

urlpatterns = [
    path("", include(router.urls)),
]
