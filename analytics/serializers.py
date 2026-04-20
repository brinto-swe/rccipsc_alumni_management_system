"""Serializers for analytics responses."""

from rest_framework import serializers


class AnalyticsOverviewSerializer(serializers.Serializer):
    total_alumni = serializers.IntegerField()
    active_users = serializers.IntegerField()
    event_participation = serializers.IntegerField()
    mentorship_matches = serializers.IntegerField()
    engagement_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
