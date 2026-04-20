"""Authentication views."""

from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from accounts.permissions import AllowPublicAuth
from accounts.serializers import CustomTokenObtainPairSerializer, LogoutSerializer
from accounts.services import record_account_audit


@extend_schema(tags=["Auth"], request=CustomTokenObtainPairSerializer, responses=CustomTokenObtainPairSerializer)
class CustomTokenObtainPairView(generics.GenericAPIView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = getattr(serializer, "user", None)
        record_account_audit(
            action="login",
            actor=user,
            target_user=user,
            message="User authenticated via JWT.",
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@extend_schema(tags=["Auth"], request=LogoutSerializer, responses={204: None})
class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [AllowPublicAuth]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if request.user.is_authenticated:
            record_account_audit(
                action="logout",
                actor=request.user,
                target_user=request.user,
                message="Refresh token blacklisted.",
                ip_address=request.META.get("REMOTE_ADDR"),
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowPublicAuth]


class CustomTokenVerifyView(TokenVerifyView):
    permission_classes = [AllowPublicAuth]
