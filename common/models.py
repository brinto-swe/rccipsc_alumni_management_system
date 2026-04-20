"""Shared abstract models and querysets."""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedQuerySet(models.QuerySet):
    """Reusable queryset helpers for timestamped models."""

    def active(self):
        if "is_deleted" in {field.name for field in self.model._meta.fields}:
            return self.filter(is_deleted=False)
        return self


class UUIDPrimaryKeyModel(models.Model):
    """Base model with a UUID primary key."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    objects = TimeStampedQuerySet.as_manager()

    class Meta:
        abstract = True


class TimeStampedModel(UUIDPrimaryKeyModel):
    """Adds created and updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditFieldsModel(TimeStampedModel):
    """Adds created_by and updated_by references for audit trails."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Adds soft delete fields for audit-friendly retention."""

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        update_fields = ["is_deleted", "deleted_at"]
        if hasattr(self, "updated_at"):
            update_fields.append("updated_at")
        self.save(update_fields=update_fields)
