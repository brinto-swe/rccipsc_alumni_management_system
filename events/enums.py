"""Enums for the event module."""

from django.db import models


class EventType(models.TextChoices):
    EFTAR_PARTY = "eftar_party", "Eftar Party"
    REUNION = "reunion", "Reunion"
    SPORTS_CARNIVAL = "sports_carnival", "Sports Carnival"
    CUSTOM = "custom_event", "Custom Event"


class PaymentMethod(models.TextChoices):
    THROUGH_ADMIN = "through_admin", "Through Admin"
    THROUGH_BATCH_STAFF = "through_batch_staff", "Through Batch Staff"
    NO_PAYMENT_REQUIRED = "no_payment_required", "No Payment Required"


class EventStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ONGOING = "ongoing", "Ongoing"
    COMPLETED = "completed", "Completed"
    ARCHIVED = "archived", "Archived"
    CANCELLED = "cancelled", "Cancelled"


class RegistrationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"
    ATTENDED = "attended", "Attended"


class PaymentStatus(models.TextChoices):
    NOT_REQUIRED = "not_required", "Not Required"
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"
