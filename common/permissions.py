"""Reusable permission helpers and role-based permission classes."""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from users.enums import UserRole


def user_has_any_role(user, *roles: str) -> bool:
    return bool(user and user.is_authenticated and user.role in roles)


def is_admin(user) -> bool:
    return user_has_any_role(user, UserRole.ADMIN)


def is_admin_or_moderator(user) -> bool:
    return user_has_any_role(user, UserRole.ADMIN, UserRole.MODERATOR)


def is_staff_or_admin(user) -> bool:
    return user_has_any_role(user, UserRole.ADMIN, UserRole.STAFF)


def is_alumni(user) -> bool:
    return user_has_any_role(user, UserRole.ALUMNI)


class ReadOnlyOrAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user)


class IsAdminOrModeratorRole(BasePermission):
    def has_permission(self, request, view):
        return is_admin_or_moderator(request.user)


class IsStaffOrAdminRole(BasePermission):
    def has_permission(self, request, view):
        return is_staff_or_admin(request.user)


class IsAlumniRole(BasePermission):
    def has_permission(self, request, view):
        return is_alumni(request.user)


class IsOwnerOrAdmin(BasePermission):
    owner_field = "user"

    def _resolve_owner(self, obj):
        value = obj
        for part in self.owner_field.split("__"):
            value = getattr(value, part, None)
            if value is None:
                return None
        return value

    def has_object_permission(self, request, view, obj):
        if is_admin(request.user):
            return True
        owner = self._resolve_owner(obj)
        return owner == request.user


class IsOwnerModeratorOrAdmin(BasePermission):
    owner_field = "user"

    def _resolve_owner(self, obj):
        value = obj
        for part in self.owner_field.split("__"):
            value = getattr(value, part, None)
            if value is None:
                return None
        return value

    def has_object_permission(self, request, view, obj):
        if is_admin_or_moderator(request.user):
            return True
        owner = self._resolve_owner(obj)
        return owner == request.user
