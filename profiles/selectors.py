"""Selectors for profile visibility and directory-safe profile access."""

from django.db.models import Prefetch, Q, QuerySet

from common.enums import VisibilityChoices
from professions.models import Profession
from profiles.models import AlumniProfile, AlumniVerificationRequest
from users.enums import UserRole


def get_profile_queryset() -> QuerySet[AlumniProfile]:
    profession_qs = Profession.objects.order_by("-currently_working_here", "-starting_date")
    return AlumniProfile.objects.select_related("user").prefetch_related(
        Prefetch("professions", queryset=profession_qs)
    )


def get_visible_profiles_for_user(user) -> QuerySet[AlumniProfile]:
    queryset = get_profile_queryset()
    if not user or not user.is_authenticated:
        return queryset.filter(directory_visibility=VisibilityChoices.PUBLIC)
    if user.role in {UserRole.ADMIN, UserRole.MODERATOR}:
        return queryset
    if user.role in {UserRole.ALUMNI, UserRole.STAFF}:
        return queryset.filter(
            Q(directory_visibility=VisibilityChoices.PUBLIC)
            | Q(directory_visibility=VisibilityChoices.ALUMNI_ONLY)
            | Q(user=user)
        )
    return queryset.filter(Q(directory_visibility=VisibilityChoices.PUBLIC) | Q(user=user))


def get_verification_request_queryset(user):
    queryset = AlumniVerificationRequest.objects.select_related("user", "reviewed_by").order_by("-created_at")
    if not user or not user.is_authenticated:
        return queryset.none()
    if user.role in {UserRole.ADMIN, UserRole.MODERATOR}:
        return queryset
    return queryset.filter(user=user)
