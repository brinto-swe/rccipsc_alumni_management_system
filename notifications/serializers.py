"""Serializers for notifications and preferences."""

from rest_framework import serializers

from notifications.models import EmailQueue, Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "is_read",
            "read_at",
            "action_url",
            "metadata",
            "sent_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["read_at", "sent_at", "created_at", "updated_at"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        exclude = ["user"]


class EmailQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailQueue
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class AdminBroadcastSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    action_url = serializers.CharField(max_length=500, required=False, allow_blank=True)
    send_email = serializers.BooleanField(default=False)
    roles = serializers.ListField(child=serializers.CharField(), required=False)
