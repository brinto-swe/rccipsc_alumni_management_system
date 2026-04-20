"""Directory permissions."""

from rest_framework.permissions import AllowAny


class CanBrowseDirectory(AllowAny):
    """Directory browsing is visibility-driven rather than auth-blocked."""
