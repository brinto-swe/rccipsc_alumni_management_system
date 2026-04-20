"""Enums for teams and team participation."""

from django.db import models


class TeamMemberRole(models.TextChoices):
    CAPTAIN = "captain", "Captain"
    PLAYER = "player", "Player"
    MANAGER = "manager", "Manager"


class TeamEventRegistrationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
