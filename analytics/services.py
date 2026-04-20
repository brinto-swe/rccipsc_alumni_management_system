"""Services for analytics snapshots."""

from django.utils import timezone

from analytics.models import AnalyticsSnapshot
from analytics.selectors import get_analytics_overview


def snapshot_today_metrics():
    overview = get_analytics_overview()
    return AnalyticsSnapshot.objects.update_or_create(
        snapshot_date=timezone.localdate(),
        defaults=overview,
    )
