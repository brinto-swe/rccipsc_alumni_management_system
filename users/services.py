"""User-domain services."""

from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from users.enums import AccountStatus, UserRole
from users.models import User


LOGIN_ALLOWED_STATUSES = {AccountStatus.ACTIVE}


def validate_user_can_login(user: User) -> None:
    if not user.is_active:
        raise ValidationError("Your account has not been activated yet.")
    if user.account_status == AccountStatus.PENDING:
        raise ValidationError("Your account is pending approval.")
    if user.account_status == AccountStatus.SUSPENDED:
        raise ValidationError("Your account has been suspended. Please contact support.")
    if user.account_status == AccountStatus.REJECTED:
        raise ValidationError("Your account request was rejected.")
    if user.account_status == AccountStatus.DEACTIVATED:
        raise ValidationError("Your account has been deactivated.")
    if user.account_status not in LOGIN_ALLOWED_STATUSES:
        raise ValidationError("Your account cannot log in right now.")


def update_user_account(actor: User, target_user: User, **changes) -> User:
    if actor.role != UserRole.ADMIN and not actor.is_superuser:
        raise PermissionDenied("Only admins can update user accounts.")

    for field, value in changes.items():
        setattr(target_user, field, value)
    target_user.updated_at = timezone.now()
    target_user.save()
    return target_user
