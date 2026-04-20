"""Enums for mentorship lifecycle."""

from django.db import models


class MentorProfileStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class MentorshipRequestStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"
    COMPLETED = "completed", "Completed"


class MentorshipSessionStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    DONE = "done", "Done"
    MISSED = "missed", "Missed"
