"""Selectors for profession access."""

from professions.models import Profession
from users.enums import UserRole


def get_profession_queryset(user):
    queryset = Profession.objects.select_related("profile", "profile__user").order_by(
        "-currently_working_here",
        "-starting_date",
    )
    if not user or not user.is_authenticated:
        return queryset.none()
    if user.role == UserRole.ADMIN:
        return queryset
    return queryset.filter(profile__user=user)
