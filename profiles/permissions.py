"""Profile-specific permissions."""

from common.permissions import IsOwnerOrAdmin


class CanManageOwnProfile(IsOwnerOrAdmin):
    owner_field = "user"
