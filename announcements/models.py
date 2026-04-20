"""Announcement and news models."""

from django.db import models
from django.utils import timezone

from announcements.enums import AnnouncementVisibility
from common.models import AuditFieldsModel
from common.utils import generate_slug


class AnnouncementCategory(AuditFieldsModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Announcement(AuditFieldsModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    content = models.TextField()
    category = models.ForeignKey(AnnouncementCategory, on_delete=models.SET_NULL, null=True, related_name="announcements")
    is_pinned = models.BooleanField(default=False, db_index=True)
    is_published = models.BooleanField(default=False, db_index=True)
    visibility = models.CharField(
        max_length=20,
        choices=AnnouncementVisibility.choices,
        default=AnnouncementVisibility.PUBLIC,
        db_index=True,
    )
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["-is_pinned", "-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["is_published", "visibility"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.title)
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

# Create your models here.
