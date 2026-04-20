"""Selectors for clubs."""

from django.db.models import Count, Q

from clubs.models import Club, ClubMembership


def get_visible_clubs(user):
    queryset = Club.objects.filter(is_active=True).annotate(memberships_count=Count("memberships", distinct=True))
    if not user or not user.is_authenticated:
        return queryset.filter(visibility="public")
    if user.role in {"admin", "moderator", "staff", "alumni"}:
        return queryset.filter(Q(visibility="public") | Q(visibility="alumni_only")).distinct()
    return queryset.filter(Q(visibility="public") | Q(visibility="private", memberships__user=user)).distinct()


def get_club_membership_queryset(user):
    queryset = ClubMembership.objects.select_related("club", "user").order_by("-created_at")
    if not user or not user.is_authenticated:
        return queryset.none()
    if user.role in {"admin", "moderator"}:
        return queryset
    return queryset.filter(user=user)
