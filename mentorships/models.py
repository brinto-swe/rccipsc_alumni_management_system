"""Mentorship models."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from common.models import AuditFieldsModel, TimeStampedModel
from mentorships.enums import MentorProfileStatus, MentorshipRequestStatus, MentorshipSessionStatus


class MentorProfile(AuditFieldsModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mentor_profile")
    professional_title = models.CharField(max_length=255)
    expertise_areas = models.JSONField(default=list, blank=True)
    bio = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=MentorProfileStatus.choices,
        default=MentorProfileStatus.PENDING,
        db_index=True,
    )
    approval_note = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_mentor_profiles",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    is_accepting_mentees = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]


class MentorshipRequest(AuditFieldsModel):
    mentor_profile = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name="requests")
    mentee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mentorship_requests")
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=MentorshipRequestStatus.choices,
        default=MentorshipRequestStatus.PENDING,
        db_index=True,
    )
    response_note = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["mentor_profile", "mentee"],
                condition=models.Q(status="pending"),
                name="unique_pending_mentorship_request",
            ),
        ]


class MentorshipSession(AuditFieldsModel):
    mentorship_request = models.ForeignKey(MentorshipRequest, on_delete=models.CASCADE, related_name="sessions")
    scheduled_at = models.DateTimeField(db_index=True)
    duration_minutes = models.PositiveIntegerField(default=60)
    meeting_link = models.URLField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=MentorshipSessionStatus.choices,
        default=MentorshipSessionStatus.SCHEDULED,
        db_index=True,
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-scheduled_at"]


class MentorshipFeedback(TimeStampedModel):
    session = models.ForeignKey(MentorshipSession, on_delete=models.CASCADE, related_name="feedback_items")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mentorship_feedback")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["session", "author"], name="unique_feedback_per_author_session"),
        ]

# Create your models here.
