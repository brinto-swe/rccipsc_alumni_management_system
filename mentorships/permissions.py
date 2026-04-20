"""Permissions for mentorship endpoints."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class CanReadMentorship(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated
