"""Profile-domain models."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from common.constants import CURRENT_YEAR_LOWER_BOUND
from common.enums import VisibilityChoices
from common.models import AuditFieldsModel, TimeStampedModel
from common.utils import upload_to
from common.validators import validate_image_upload
from profiles.enums import AcademicGroup, VerificationRequestStatus


class AlumniProfile(AuditFieldsModel):
    """Extends the user account with alumni and privacy information."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    full_name = models.CharField(max_length=255, blank=True, db_index=True)
    student_id = models.CharField(max_length=100, blank=True, db_index=True)
    class_roll = models.CharField(max_length=100, blank=True, db_index=True)
    batch_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(CURRENT_YEAR_LOWER_BOUND),
            MaxValueValidator(timezone.now().year + 5),
        ],
        db_index=True,
        help_text="Primary batch/search year used in directory filters.",
    )
    academic_group = models.CharField(
        max_length=30,
        choices=AcademicGroup.choices,
        blank=True,
        db_index=True,
    )
    ssc_passing_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(CURRENT_YEAR_LOWER_BOUND),
            MaxValueValidator(timezone.now().year + 5),
        ],
    )
    ssc_school_name = models.CharField(max_length=255, blank=True)
    hsc_passing_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(CURRENT_YEAR_LOWER_BOUND),
            MaxValueValidator(timezone.now().year + 5),
        ],
    )
    hsc_school_name = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to=upload_to("profiles", "pictures"),
        blank=True,
        null=True,
        validators=[validate_image_upload],
    )
    phone_number = models.CharField(max_length=30, blank=True)
    present_address = models.TextField(blank=True)
    permanent_address = models.TextField(blank=True)
    current_city = models.CharField(max_length=150, blank=True, db_index=True)
    current_country = models.CharField(max_length=150, blank=True, db_index=True)
    social_links = models.JSONField(default=dict, blank=True)
    directory_visibility = models.CharField(
        max_length=20,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.ALUMNI_ONLY,
        db_index=True,
    )
    email_visibility = models.CharField(
        max_length=20,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.ALUMNI_ONLY,
    )
    phone_visibility = models.CharField(
        max_length=20,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.PRIVATE,
    )
    social_link_visibility = models.CharField(
        max_length=20,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.PUBLIC,
    )

    class Meta:
        ordering = ["full_name", "created_at"]
        indexes = [
            models.Index(fields=["batch_year", "academic_group"]),
            models.Index(fields=["current_city", "current_country"]),
            models.Index(fields=["directory_visibility"]),
        ]

    def __str__(self) -> str:
        return self.full_name or self.user.email

    def clean(self):
        if self.ssc_passing_year and self.hsc_passing_year and self.hsc_passing_year < self.ssc_passing_year:
            raise ValidationError("HSC passing year cannot be earlier than SSC passing year.")


class AlumniVerificationRequest(TimeStampedModel):
    """Request for official alumni/member verification."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification_requests",
    )
    status = models.CharField(
        max_length=20,
        choices=VerificationRequestStatus.choices,
        default=VerificationRequestStatus.PENDING,
        db_index=True,
    )
    note = models.TextField(blank=True)
    review_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_verification_requests",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "status"])]

    def __str__(self) -> str:
        return f"{self.user.email} - {self.status}"
