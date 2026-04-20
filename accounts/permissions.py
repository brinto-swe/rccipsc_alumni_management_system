"""Account-specific permissions."""

from rest_framework.permissions import AllowAny


class AllowPublicAuth(AllowAny):
    """Explicit alias for auth endpoints."""
