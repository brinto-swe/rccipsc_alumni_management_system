"""Notification, preference, and email queue models."""

from django.conf import settings
from django.db import models

from common.models import AuditFieldsModel, TimeStampedModel
from notifications.enums import EmailQueueStatus, NotificationType


class Notification(TimeStampedModel):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NotificationType.choices, db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class NotificationPreference(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preference",
    )
    in_app_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    event_reminders = models.BooleanField(default=True)
    mentorship_updates = models.BooleanField(default=True)
    admin_broadcasts = models.BooleanField(default=True)
    connection_updates = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"Notification preferences for {self.user}"


class EmailQueue(AuditFieldsModel):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="queued_emails",
    )
    recipient_email = models.EmailField(db_index=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=EmailQueueStatus.choices,
        default=EmailQueueStatus.PENDING,
        db_index=True,
    )
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

# Create your models here.
