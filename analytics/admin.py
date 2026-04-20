from django.contrib import admin

from analytics.models import AnalyticsSnapshot


@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ["snapshot_date", "total_alumni", "active_users", "event_participation", "engagement_rate"]
    ordering = ["-snapshot_date"]
