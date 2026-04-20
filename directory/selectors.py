"""Selectors for the alumni directory module."""

from django.db.models import Q

from profiles.selectors import get_visible_profiles_for_user


def get_directory_queryset(user):
    return (
        get_visible_profiles_for_user(user)
        .filter(user__role="alumni", user__account_status="active")
        .distinct()
    )


def get_suggested_alumni_queryset(user):
    queryset = get_directory_queryset(user)
    if not user or not user.is_authenticated or not hasattr(user, "profile"):
        return queryset[:10]

    profile = user.profile
    return (
        queryset.exclude(user=user)
        .filter(
            Q(batch_year=profile.batch_year)
            | Q(academic_group=profile.academic_group)
            | Q(current_city=profile.current_city)
        )
        .distinct()[:10]
    )
