"""Profile-specific enums."""

from django.db import models


class AcademicGroup(models.TextChoices):
    SCIENCE = "science", "Science"
    BUSINESS_STUDIES = "business_studies", "Business Studies"
    HUMANITIES = "humanities", "Humanities"


class VerificationRequestStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
