"""Notification-related enums."""

from django.db import models


class NotificationType(models.TextChoices):
    EVENT_REGISTRATION = "event_registration", "Event Registration"
    EVENT_REMINDER = "event_reminder", "Event Reminder"
    MENTORSHIP_UPDATE = "mentorship_update", "Mentorship Update"
    CONNECTION_ACCEPTED = "connection_accepted", "Connection Accepted"
    ADMIN_BROADCAST = "admin_broadcast", "Admin Broadcast"
    SYSTEM = "system", "System"


class EmailQueueStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
