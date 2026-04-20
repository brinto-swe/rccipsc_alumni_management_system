"""Enums for announcement visibility."""

from django.db import models


class AnnouncementVisibility(models.TextChoices):
    PUBLIC = "public", "Public"
    ALUMNI_ONLY = "alumni_only", "Alumni Only"
    STAFF_ONLY = "staff_only", "Staff Only"
