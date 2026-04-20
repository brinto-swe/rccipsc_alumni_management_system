"""Shared enums used by multiple apps."""

from django.db import models


class VisibilityChoices(models.TextChoices):
    PUBLIC = "public", "Public"
    ALUMNI_ONLY = "alumni_only", "Alumni Only"
    PRIVATE = "private", "Private"


class PublicationStatusChoices(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class ModerationStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    REMOVED = "removed", "Removed"


class ChannelChoices(models.TextChoices):
    IN_APP = "in_app", "In-App"
    EMAIL = "email", "Email"
