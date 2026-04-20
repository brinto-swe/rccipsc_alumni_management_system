"""Selectors for account-oriented read flows."""

from accounts.models import AccountAuditLog


def get_account_audit_queryset():
    return AccountAuditLog.objects.select_related("actor", "target_user").order_by("-created_at")
