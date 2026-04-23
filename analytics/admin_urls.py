"""Admin analytics URL patterns."""

from django.urls import include, path

from analytics.views import AdminDashboardOverviewAPIView, AdminSystemOverviewAPIView

urlpatterns = [
    path("dashboard/overview/", AdminDashboardOverviewAPIView.as_view(), name="admin-dashboard-overview"),
    path("settings/overview/", AdminSystemOverviewAPIView.as_view(), name="admin-system-overview"),
    path("analytics/", include("analytics.urls")),
]
