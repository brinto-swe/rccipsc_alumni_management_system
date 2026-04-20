"""Enums for clubs and memberships."""

from django.db import models


class ClubMembershipRole(models.TextChoices):
    MEMBER = "member", "Member"
    COORDINATOR = "coordinator", "Coordinator"
    LEAD = "lead", "Lead"


class ClubMembershipStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    PENDING = "pending", "Pending"
    INACTIVE = "inactive", "Inactive"
