"""Services for creating notifications and queuing email."""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from notifications.enums import NotificationType
from notifications.models import EmailQueue, Notification, NotificationPreference


User = get_user_model()


def _get_or_create_preference(user):
    preference, _ = NotificationPreference.objects.get_or_create(user=user)
    return preference


def create_notification(*, recipient, title: str, message: str, notification_type: str, action_url: str = "", metadata=None):
    preference = _get_or_create_preference(recipient)
    if not preference.in_app_enabled:
        return None
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        action_url=action_url,
        metadata=metadata or {},
        sent_at=timezone.now(),
    )


def queue_email_message(*, recipient, subject: str, body: str, metadata=None, scheduled_for=None):
    preference = _get_or_create_preference(recipient)
    if not preference.email_enabled:
        return None
    return EmailQueue.objects.create(
        recipient=recipient,
        recipient_email=recipient.email,
        subject=subject,
        body=body,
        metadata=metadata or {},
        scheduled_for=scheduled_for,
    )


def mark_notification_as_read(*, actor, notification):
    if notification.recipient_id != actor.id and actor.role != "admin":
        raise PermissionDenied("You can only mark your own notifications as read.")
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save(update_fields=["is_read", "read_at", "updated_at"])
    return notification


@transaction.atomic
def create_admin_broadcast(*, actor, title: str, message: str, action_url: str = "", send_email: bool = False, roles=None):
    if actor.role not in {"admin", "moderator"}:
        raise PermissionDenied("Only admins or moderators can send broadcasts.")
    queryset = User.objects.filter(is_active=True)
    if roles:
        queryset = queryset.filter(role__in=roles)

    notifications = []
    for recipient in queryset.iterator():
        notification = create_notification(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=NotificationType.ADMIN_BROADCAST,
            action_url=action_url,
            metadata={"broadcast_by": str(actor.id)},
        )
        notifications.append(notification)
        if send_email:
            queue_email_message(
                recipient=recipient,
                subject=title,
                body=message,
                metadata={"broadcast_by": str(actor.id)},
            )
    return notifications
