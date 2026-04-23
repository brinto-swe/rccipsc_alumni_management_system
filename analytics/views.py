"""Analytics API views."""
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.selectors import get_admin_dashboard_overview, get_admin_system_overview, get_analytics_overview
from analytics.serializers import (
    AdminDashboardOverviewSerializer,
    AdminSystemOverviewSerializer,
    AnalyticsOverviewSerializer,
)


@extend_schema(tags=["Analytics"], responses=AnalyticsOverviewSerializer)
class AnalyticsOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.role not in {"admin", "moderator"}:
            return Response({"detail": "Only admins or moderators can view analytics."}, status=403)
        data = get_analytics_overview()
        return Response(AnalyticsOverviewSerializer(data).data)


@extend_schema(tags=["Analytics"], responses=AdminDashboardOverviewSerializer)
class AdminDashboardOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.role not in {"admin", "moderator", "staff"}:
            return Response({"detail": "Only operations roles can view the admin dashboard."}, status=403)
        data = get_admin_dashboard_overview(request.user.role)
        return Response(AdminDashboardOverviewSerializer(data).data)


@extend_schema(tags=["Analytics"], responses=AdminSystemOverviewSerializer)
class AdminSystemOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.role != "admin":
            return Response({"detail": "Only admins can view system settings overview."}, status=403)
        data = get_admin_system_overview()
        return Response(AdminSystemOverviewSerializer(data).data)
