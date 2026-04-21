"""Event-domain models."""

from datetime import datetime, time as dt_time

from cloudinary.models import CloudinaryField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from common.enums import ModerationStatusChoices, VisibilityChoices
from common.models import AuditFieldsModel, TimeStampedModel
from common.validators import validate_document_upload, validate_image_upload
from events.enums import EventStatus, EventType, PaymentMethod, PaymentStatus, RegistrationStatus
from events.validators import validate_event_dates, validate_event_type_requirements


class Event(AuditFieldsModel):
    """Represents all event types through a single extensible table."""

    event_type = models.CharField(max_length=30, choices=EventType.choices, db_index=True)
    event_name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=280, unique=True)
    banner = CloudinaryField(
        "image",
        blank=True,
        null=True,
        folder="events/banners",
        validators=[validate_image_upload],
    )
    invitation_letter = models.TextField(blank=True)
    batch = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    season = models.CharField(max_length=100, blank=True, db_index=True)
    year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(2000),
            MaxValueValidator(timezone.now().year + 5),
        ],
        db_index=True,
    )
    event_date = models.DateField(null=True, blank=True, db_index=True)
    event_start_date = models.DateTimeField(null=True, blank=True, db_index=True)
    event_end_date = models.DateTimeField(null=True, blank=True, db_index=True)
    location = models.CharField(max_length=255, db_index=True)
    gathering_time = models.TimeField(null=True, blank=True)
    registration_start_date = models.DateTimeField(null=True, blank=True)
    registration_end_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.NO_PAYMENT_REQUIRED,
        db_index=True,
    )
    generate_registration_pdf = models.BooleanField(default=False)
    generate_ticket_or_checkin_pdf = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.DRAFT,
        db_index=True,
    )
    is_public = models.BooleanField(default=True, db_index=True)
    creator_role = models.CharField(max_length=20, blank=True)
    sponsor_support_enabled = models.BooleanField(default=False)
    participant_visibility = models.CharField(
        max_length=20,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.PUBLIC,
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-event_start_date", "-event_date", "-created_at"]
        indexes = [
            models.Index(fields=["event_type", "status"]),
            models.Index(fields=["batch", "event_date"]),
            models.Index(fields=["is_public", "status"]),
            models.Index(fields=["registration_start_date", "registration_end_date"]),
        ]

    def __str__(self) -> str:
        return self.event_name

    def clean(self):
        validate_event_dates(self)
        validate_event_type_requirements(self)

    @property
    def effective_start(self):
        return self.event_start_date or (
            timezone.make_aware(
                datetime.combine(self.event_date, self.gathering_time or dt_time.min)
            )
            if self.event_date
            else None
        )

    def is_registration_open(self) -> bool:
        now = timezone.now()
        return bool(
            self.registration_start_date
            and self.registration_end_date
            and self.registration_start_date <= now <= self.registration_end_date
        )

    def has_started(self) -> bool:
        start = self.effective_start
        return bool(start and start <= timezone.now())

    def has_ended(self) -> bool:
        end = self.event_end_date or self.effective_start
        return bool(end and end <= timezone.now())


class EventSponsor(AuditFieldsModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="sponsors")
    sponsor_name = models.CharField(max_length=255, db_index=True)
    sponsor_logo = CloudinaryField(
        "image",
        blank=True,
        null=True,
        folder="events/sponsors",
        validators=[validate_image_upload],
    )

    class Meta:
        ordering = ["sponsor_name"]

    def __str__(self) -> str:
        return self.sponsor_name


class EventRegistration(TimeStampedModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_registrations",
    )
    status = models.CharField(
        max_length=20,
        choices=RegistrationStatus.choices,
        default=RegistrationStatus.PENDING,
        db_index=True,
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.NOT_REQUIRED,
        db_index=True,
    )
    payment_reference = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)
    attendee_visibility = models.CharField(
        max_length=20,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.PUBLIC,
    )
    ticket_code = models.CharField(max_length=100, blank=True, db_index=True)
    pdf_generated_at = models.DateTimeField(null=True, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["event", "user"], name="unique_event_registration"),
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.event}"


class EventGallery(AuditFieldsModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="gallery_items")
    image = CloudinaryField(
        "image",
        folder="events/gallery",
        validators=[validate_image_upload],
    )
    caption = models.CharField(max_length=255, blank=True)
    is_public = models.BooleanField(default=True, db_index=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "created_at"]


class EventResult(AuditFieldsModel):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="result")
    result_summary = models.TextField()
    highlights = models.JSONField(default=list, blank=True)
    post_event_information = models.TextField(blank=True)
    attachment = CloudinaryField(
        "raw",
        blank=True,
        null=True,
        folder="events/results",
        resource_type="raw",
        validators=[validate_document_upload],
    )

    def __str__(self) -> str:
        return f"Result - {self.event}"


class EventReview(AuditFieldsModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_reviews",
    )
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    moderation_status = models.CharField(
        max_length=20,
        choices=ModerationStatusChoices.choices,
        default=ModerationStatusChoices.APPROVED,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["event", "user"], name="unique_event_review_per_user"),
        ]

    def clean(self):
        if not self.event.has_ended():
            raise ValidationError("Reviews can only be posted after the event has ended.")
