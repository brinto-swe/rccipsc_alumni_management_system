"""Permissions for announcements."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class CanReadAnnouncements(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated
