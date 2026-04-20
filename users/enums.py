"""User-domain enums."""

from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    MODERATOR = "moderator", "Moderator"
    STAFF = "staff", "Staff"
    ALUMNI = "alumni", "Alumni"
    GUEST = "guest", "Guest User / Current Student"


class AccountStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    REJECTED = "rejected", "Rejected"
    DEACTIVATED = "deactivated", "Deactivated"
