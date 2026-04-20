"""Authentication and account-side services."""

from accounts.models import AccountAuditLog


def record_account_audit(*, action: str, actor=None, target_user=None, message: str = "", metadata=None, ip_address=None):
    return AccountAuditLog.objects.create(
        action=action,
        actor=actor,
        target_user=target_user,
        message=message,
        metadata=metadata or {},
        ip_address=ip_address,
    )
