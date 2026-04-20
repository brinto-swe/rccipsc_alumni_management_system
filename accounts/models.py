"""Authentication and account audit models."""

from django.conf import settings
from django.db import models

from common.models import TimeStampedModel


class AccountAuditLog(TimeStampedModel):
    """Stores important account and auth events for audit-friendly operations."""

    action = models.CharField(max_length=100, db_index=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_account_audits",
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="account_audit_logs",
    )
    message = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} -> {self.target_user or 'unknown'}"
