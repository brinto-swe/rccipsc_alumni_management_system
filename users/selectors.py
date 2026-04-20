"""Query selectors for the user domain."""

from django.db.models import QuerySet

from users.enums import UserRole
from users.models import User


def get_user_queryset() -> QuerySet[User]:
    return User.objects.select_related("profile").order_by("-created_at")


def get_admin_user_queryset() -> QuerySet[User]:
    return get_user_queryset()


def get_active_alumni_queryset() -> QuerySet[User]:
    return get_user_queryset().filter(
        role=UserRole.ALUMNI,
        is_active=True,
    )
