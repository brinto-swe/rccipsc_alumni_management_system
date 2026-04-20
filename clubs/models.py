"""Models for clubs and club memberships."""

from django.conf import settings
from django.db import models

from common.enums import VisibilityChoices
from common.models import AuditFieldsModel, TimeStampedModel
from common.utils import generate_slug
from clubs.enums import ClubMembershipRole, ClubMembershipStatus


class Club(AuditFieldsModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    visibility = models.CharField(
        max_length=20,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.PUBLIC,
        db_index=True,
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class ClubMembership(TimeStampedModel):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="club_memberships")
    membership_role = models.CharField(
        max_length=20,
        choices=ClubMembershipRole.choices,
        default=ClubMembershipRole.MEMBER,
    )
    status = models.CharField(
        max_length=20,
        choices=ClubMembershipStatus.choices,
        default=ClubMembershipStatus.ACTIVE,
        db_index=True,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["club", "user"], name="unique_club_membership"),
        ]

# Create your models here.
