"""Profession-domain models."""

from django.core.exceptions import ValidationError
from django.db import models

from common.models import AuditFieldsModel
from common.validators import validate_end_date_not_before_start


class Profession(AuditFieldsModel):
    """Professional history entry for an alumni profile."""

    profile = models.ForeignKey(
        "profiles.AlumniProfile",
        on_delete=models.CASCADE,
        related_name="professions",
    )
    present_occupation = models.CharField(max_length=255, db_index=True)
    role = models.CharField(max_length=255, db_index=True)
    institution_or_organization_name = models.CharField(max_length=255, db_index=True)
    starting_date = models.DateField()
    ending_date = models.DateField(null=True, blank=True)
    currently_working_here = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-currently_working_here", "-starting_date", "-created_at"]
        indexes = [
            models.Index(fields=["present_occupation", "currently_working_here"]),
            models.Index(fields=["institution_or_organization_name"]),
        ]

    def __str__(self) -> str:
        return f"{self.profile} - {self.present_occupation}"

    def clean(self):
        validate_end_date_not_before_start(self.starting_date, self.ending_date, "Profession")
        if self.currently_working_here and self.ending_date:
            raise ValidationError("Ending date must be empty when currently working here is true.")
        if not self.currently_working_here and not self.ending_date:
            raise ValidationError("Ending date is required unless currently working here is true.")
