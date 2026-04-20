"""Enums for the social feed module."""

from django.db import models


class PostVisibility(models.TextChoices):
    PUBLIC = "public", "Public"
    AUTHENTICATED = "authenticated", "Authenticated Users"
    ALUMNI_ONLY = "alumni_only", "Alumni Community"


class ReactionType(models.TextChoices):
    LIKE = "like", "Like"
    DISLIKE = "dislike", "Dislike"


class ReportStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    IN_REVIEW = "in_review", "In Review"
    RESOLVED = "resolved", "Resolved"
    DISMISSED = "dismissed", "Dismissed"
