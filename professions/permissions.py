"""Profession-specific permissions."""

from common.permissions import IsOwnerOrAdmin


class CanManageOwnProfession(IsOwnerOrAdmin):
    owner_field = "profile__user"
