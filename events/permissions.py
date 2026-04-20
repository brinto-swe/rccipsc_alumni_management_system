"""Permissions for event workflows."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class CanReadVisibleEvents(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated


class IsEventManager(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == "admin":
            return True
        return obj.created_by_id == request.user.id
