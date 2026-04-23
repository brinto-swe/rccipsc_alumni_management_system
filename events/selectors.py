"""Selectors for event queries."""

from django.db.models import Count, Prefetch, Q
from django.utils import timezone

from events.enums import EventStatus
from events.models import Event, EventGallery, EventRegistration, EventReview


def get_event_queryset():
    return (
        Event.objects.select_related("created_by", "updated_by", "result")
        .prefetch_related("sponsors", "gallery_items", Prefetch("reviews", queryset=EventReview.objects.select_related("user")))
        .annotate(registration_count=Count("registrations", distinct=True))
    )


def get_visible_event_queryset(user):
    queryset = get_event_queryset().distinct()
    public_condition = Q(is_public=True, status__in=[EventStatus.PUBLISHED, EventStatus.ONGOING, EventStatus.COMPLETED, EventStatus.ARCHIVED])
    if not user or not user.is_authenticated:
        return queryset.filter(public_condition)
    if user.role == "admin":
        return queryset
    if user.role in {"moderator", "staff", "alumni"}:
        return queryset.filter(public_condition | Q(is_public=False) | Q(created_by=user))
    return queryset.filter(public_condition | Q(registrations__user=user))


def get_previous_event_queryset(user):
    now = timezone.now()
    return get_visible_event_queryset(user).filter(
        Q(event_end_date__lt=now)
        | Q(event_date__lt=now.date())
        | Q(status__in=[EventStatus.COMPLETED, EventStatus.ARCHIVED])
    ).distinct()


def get_registration_queryset(user):
    queryset = EventRegistration.objects.select_related("event", "user").order_by("-created_at")
    if not user or not user.is_authenticated:
        return queryset.none()
    if user.role == "admin":
        return queryset
    if user.role == "staff":
        return queryset.filter(Q(event__created_by=user) | Q(user=user)).distinct()
    return queryset.filter(user=user)


def get_gallery_queryset(user):
    queryset = EventGallery.objects.select_related("event", "created_by").order_by("display_order", "-created_at")
    if not user or not user.is_authenticated:
        return queryset.filter(is_public=True, event__is_public=True)
    if user.role == "admin":
        return queryset
    return queryset.filter(Q(is_public=True) | Q(event__created_by=user))
