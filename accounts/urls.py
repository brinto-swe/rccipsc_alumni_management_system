"""Authentication URL patterns."""

from django.urls import include, path

from accounts.views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    LogoutAPIView,
)


urlpatterns = [
    path("jwt/create/", CustomTokenObtainPairView.as_view(), name="jwt-create"),
    path("jwt/refresh/", CustomTokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", CustomTokenVerifyView.as_view(), name="jwt-verify"),
    path("logout/", LogoutAPIView.as_view(), name="jwt-logout"),
    path("", include("djoser.urls")),
]
