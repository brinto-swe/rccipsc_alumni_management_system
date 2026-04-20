"""User-specific permissions."""

from common.permissions import IsAdminRole


class CanManageUsers(IsAdminRole):
    """Alias permission for clearer intent in admin user endpoints."""
