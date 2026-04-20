"""Selectors for published announcements."""

from django.db.models import Q

from announcements.models import Announcement, AnnouncementCategory


def get_visible_announcements(user):
    queryset = Announcement.objects.select_related("category", "created_by").order_by("-is_pinned", "-published_at")
    if not user or not user.is_authenticated:
        return queryset.filter(is_published=True, visibility="public")
    if user.role in {"admin", "moderator", "staff"}:
        return queryset
    if user.role == "alumni":
        return queryset.filter(
            Q(is_published=True, visibility="public")
            | Q(is_published=True, visibility="alumni_only")
        )
    return queryset.filter(is_published=True, visibility="public")


def get_announcement_categories():
    return AnnouncementCategory.objects.order_by("name")
