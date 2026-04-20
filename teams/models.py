"""Team and sports participation models."""

from django.conf import settings
from django.db import models

from common.models import AuditFieldsModel, TimeStampedModel
from teams.enums import TeamEventRegistrationStatus, TeamMemberRole


class Team(AuditFieldsModel):
    name = models.CharField(max_length=255)
    sport_type = models.CharField(max_length=120, db_index=True)
    batch_year = models.PositiveIntegerField(db_index=True)
    description = models.TextField(blank=True)
    captain = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="captained_teams",
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["name", "batch_year"], name="unique_team_per_batch"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.batch_year})"


class TeamMember(TimeStampedModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="team_memberships")
    role = models.CharField(max_length=20, choices=TeamMemberRole.choices, default=TeamMemberRole.PLAYER)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["team", "user"], name="unique_team_member"),
        ]


class TeamEventRegistration(AuditFieldsModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="event_registrations")
    event = models.ForeignKey("events.Event", on_delete=models.CASCADE, related_name="team_registrations")
    status = models.CharField(
        max_length=20,
        choices=TeamEventRegistrationStatus.choices,
        default=TeamEventRegistrationStatus.PENDING,
        db_index=True,
    )
    note = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["team", "event"], name="unique_team_event_registration"),
        ]

# Create your models here.
