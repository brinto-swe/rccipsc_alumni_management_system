"""Shared API views."""

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


@extend_schema(tags=["System"], responses={200: dict})
class HealthCheckAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"})
