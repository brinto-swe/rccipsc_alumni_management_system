"""Selectors for notification views."""

from notifications.models import EmailQueue, Notification


def get_notification_queryset(user):
    queryset = Notification.objects.order_by("-created_at")
    if not user or not user.is_authenticated:
        return queryset.none()
    return queryset.filter(recipient=user)


def get_email_queue_queryset(user):
    queryset = EmailQueue.objects.select_related("recipient", "created_by").order_by("-created_at")
    if not user or not user.is_authenticated:
        return queryset.none()
    if user.role == "admin":
        return queryset
    return queryset.none()
