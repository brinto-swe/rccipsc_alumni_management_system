"""Services for announcement management."""

from rest_framework.exceptions import PermissionDenied

from announcements.models import Announcement, AnnouncementCategory


def create_announcement(*, actor, validated_data):
    if actor.role not in {"admin", "moderator"}:
        raise PermissionDenied("Only admins or moderators can create announcements.")
    return Announcement.objects.create(created_by=actor, updated_by=actor, **validated_data)


def update_announcement(*, actor, announcement: Announcement, validated_data):
    if actor.role not in {"admin", "moderator"}:
        raise PermissionDenied("Only admins or moderators can update announcements.")
    for field, value in validated_data.items():
        setattr(announcement, field, value)
    announcement.updated_by = actor
    announcement.save()
    return announcement


def create_category(*, actor, validated_data):
    if actor.role not in {"admin", "moderator"}:
        raise PermissionDenied("Only admins or moderators can create categories.")
    return AnnouncementCategory.objects.create(created_by=actor, updated_by=actor, **validated_data)
