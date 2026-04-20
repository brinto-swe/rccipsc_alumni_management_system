"""User-domain models."""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from common.constants import CURRENT_YEAR_LOWER_BOUND
from common.models import TimeStampedModel
from users.enums import AccountStatus, UserRole
from users.managers import UserManager


class User(TimeStampedModel, AbstractBaseUser, PermissionsMixin):
    """Custom user model using email as the login identifier."""

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, db_index=True)
    account_status = models.CharField(
        max_length=20,
        choices=AccountStatus.choices,
        default=AccountStatus.PENDING,
        db_index=True,
    )
    managed_batch_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(CURRENT_YEAR_LOWER_BOUND),
            MaxValueValidator(timezone.now().year + 5),
        ],
        db_index=True,
        help_text="Used for batch-wise staff scoping.",
    )
    is_active = models.BooleanField(default=False, db_index=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(
        default=False,
        help_text="Institution or moderator verified alumni/member flag.",
    )
    date_joined = models.DateTimeField(default=timezone.now, db_index=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["role", "account_status"]),
            models.Index(fields=["is_active", "is_verified"]),
            models.Index(fields=["managed_batch_year"]),
        ]

    def __str__(self) -> str:
        return self.email

    @property
    def full_display_name(self) -> str:
        if hasattr(self, "profile") and self.profile.full_name:
            return self.profile.full_name
        return self.username or self.email
