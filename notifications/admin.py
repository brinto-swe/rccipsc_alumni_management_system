from django.contrib import admin

from notifications.models import EmailQueue, Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["recipient", "title", "notification_type", "is_read", "created_at"]
    search_fields = ["recipient__email", "title", "message"]
    list_filter = ["notification_type", "is_read", "created_at"]


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ["user", "in_app_enabled", "email_enabled", "event_reminders", "mentorship_updates"]
    search_fields = ["user__email"]


@admin.register(EmailQueue)
class EmailQueueAdmin(admin.ModelAdmin):
    list_display = ["recipient_email", "subject", "status", "scheduled_for", "sent_at"]
    search_fields = ["recipient_email", "subject"]
    list_filter = ["status", "scheduled_for", "sent_at"]
