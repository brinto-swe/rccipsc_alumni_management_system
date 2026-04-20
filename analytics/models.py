"""Simple persisted analytics snapshot model for future scheduled aggregation."""

from django.db import models

from common.models import TimeStampedModel


class AnalyticsSnapshot(TimeStampedModel):
    snapshot_date = models.DateField(unique=True, db_index=True)
    total_alumni = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    event_participation = models.PositiveIntegerField(default=0)
    mentorship_matches = models.PositiveIntegerField(default=0)
    engagement_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-snapshot_date"]

# Create your models here.
