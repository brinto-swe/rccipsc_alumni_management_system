"""Selectors for mentorship read flows."""

from django.db.models import Q

from mentorships.models import MentorProfile, MentorshipFeedback, MentorshipRequest, MentorshipSession


def get_mentor_queryset(user):
    queryset = MentorProfile.objects.select_related("user").order_by("-created_at")
    if not user or not user.is_authenticated:
        return queryset.filter(status="approved", is_accepting_mentees=True)
    if user.role == "admin":
        return queryset
    return queryset.filter(Q(status="approved") | Q(user=user))


def get_mentorship_request_queryset(user):
    queryset = MentorshipRequest.objects.select_related("mentor_profile", "mentor_profile__user", "mentee").order_by("-created_at")
    if not user or not user.is_authenticated:
        return queryset.none()
    if user.role == "admin":
        return queryset
    return queryset.filter(Q(mentee=user) | Q(mentor_profile__user=user))


def get_mentorship_session_queryset(user):
    queryset = MentorshipSession.objects.select_related("mentorship_request", "mentorship_request__mentor_profile", "mentorship_request__mentee").order_by("-scheduled_at")
    if not user or not user.is_authenticated:
        return queryset.none()
    if user.role == "admin":
        return queryset
    return queryset.filter(
        Q(mentorship_request__mentee=user) | Q(mentorship_request__mentor_profile__user=user)
    )


def get_mentorship_feedback_queryset(user):
    queryset = MentorshipFeedback.objects.select_related("session", "author").order_by("-created_at")
    if not user or not user.is_authenticated:
        return queryset.none()
    if user.role == "admin":
        return queryset
    return queryset.filter(
        Q(author=user)
        | Q(session__mentorship_request__mentee=user)
        | Q(session__mentorship_request__mentor_profile__user=user)
    )
