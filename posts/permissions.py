"""Permissions for post and moderation endpoints."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class CanReadPosts(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated


class IsModeratorOrAdminContentManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {"admin", "moderator"}
