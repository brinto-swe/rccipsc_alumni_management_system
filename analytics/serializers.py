"""Serializers for analytics responses."""

from rest_framework import serializers


class AnalyticsOverviewSerializer(serializers.Serializer):
    total_alumni = serializers.IntegerField()
    active_users = serializers.IntegerField()
    event_participation = serializers.IntegerField()
    mentorship_matches = serializers.IntegerField()
    engagement_rate = serializers.DecimalField(max_digits=5, decimal_places=2)


class AdminDashboardStatSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.IntegerField()
    meta = serializers.CharField()
    tone = serializers.CharField()
    tag = serializers.CharField()


class AdminDashboardActivitySerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    meta = serializers.CharField()
    badge = serializers.CharField(required=False, allow_blank=True)
    tone = serializers.CharField(required=False, allow_blank=True)


class AdminDashboardChartPointSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.IntegerField()


class AdminDashboardChartSerializer(serializers.Serializer):
    title = serializers.CharField()
    subtitle = serializers.CharField()
    points = AdminDashboardChartPointSerializer(many=True)


class AdminDashboardOverviewSerializer(serializers.Serializer):
    role = serializers.CharField()
    stats = AdminDashboardStatSerializer(many=True)
    recent_activity = AdminDashboardActivitySerializer(many=True)
    review_queue = AdminDashboardActivitySerializer(many=True)
    charts = AdminDashboardChartSerializer(many=True)


class AdminSystemOverviewSerializer(serializers.Serializer):
    site_name = serializers.CharField()
    default_domain = serializers.CharField()
    frontend_url = serializers.CharField()
    docs_url = serializers.CharField()
    cloudinary_enabled = serializers.BooleanField()
    email_backend = serializers.CharField()
    timezone = serializers.CharField()
    default_page_size = serializers.IntegerField()
    role_matrix = serializers.DictField(child=serializers.ListField(child=serializers.CharField()))
