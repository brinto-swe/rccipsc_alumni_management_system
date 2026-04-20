"""Permissions for notification endpoints."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class CanAccessOwnNotifications(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsAdminOrModeratorNotifier(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {"admin", "moderator"}
