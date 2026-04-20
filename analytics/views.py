"""Analytics API views."""

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.selectors import get_analytics_overview
from analytics.serializers import AnalyticsOverviewSerializer


@extend_schema(tags=["Analytics"], responses=AnalyticsOverviewSerializer)
class AnalyticsOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.role not in {"admin", "moderator"}:
            return Response({"detail": "Only admins or moderators can view analytics."}, status=403)
        data = get_analytics_overview()
        return Response(AnalyticsOverviewSerializer(data).data)
