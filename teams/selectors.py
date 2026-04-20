"""Selectors for team visibility and management."""

from django.db.models import Count

from teams.models import Team, TeamEventRegistration, TeamMember


def get_team_queryset(user):
    queryset = Team.objects.annotate(members_count=Count("members", distinct=True)).select_related("captain", "created_by")
    if not user or not user.is_authenticated:
        return queryset.filter(is_active=True)
    if user.role == "admin":
        return queryset
    if user.role == "staff":
        return queryset.filter(batch_year=user.managed_batch_year)
    return queryset.filter(is_active=True)


def get_team_member_queryset(user):
    queryset = TeamMember.objects.select_related("team", "user").order_by("-created_at")
    if not user or not user.is_authenticated:
        return queryset.none()
    if user.role == "admin":
        return queryset
    if user.role == "staff":
        return queryset.filter(team__batch_year=user.managed_batch_year)
    return queryset.filter(user=user)


def get_team_event_registration_queryset(user):
    queryset = TeamEventRegistration.objects.select_related("team", "event", "created_by").order_by("-created_at")
    if not user or not user.is_authenticated:
        return queryset.none()
    if user.role == "admin":
        return queryset
    if user.role == "staff":
        return queryset.filter(team__batch_year=user.managed_batch_year)
    return queryset.filter(team__members__user=user).distinct()
