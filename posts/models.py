"""Models for posts, comments, reactions, and reports."""

from cloudinary.models import CloudinaryField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from common.enums import ModerationStatusChoices
from common.models import AuditFieldsModel, SoftDeleteModel, TimeStampedModel
from common.validators import validate_image_upload
from posts.enums import PostVisibility, ReactionType, ReportStatus


class Post(SoftDeleteModel, AuditFieldsModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    content = models.TextField()
    visibility = models.CharField(
        max_length=20,
        choices=PostVisibility.choices,
        default=PostVisibility.PUBLIC,
        db_index=True,
    )
    moderation_status = models.CharField(
        max_length=20,
        choices=ModerationStatusChoices.choices,
        default=ModerationStatusChoices.APPROVED,
        db_index=True,
    )
    is_published = models.BooleanField(default=True, db_index=True)
    is_comments_enabled = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["visibility", "is_published"]),
            models.Index(fields=["author", "published_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.author} - {self.published_at:%Y-%m-%d}"


class PostMedia(AuditFieldsModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media_items")
    image = CloudinaryField(
        "image",
        folder="posts/media",
        validators=[validate_image_upload],
    )
    caption = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["created_at"]


class Comment(SoftDeleteModel, AuditFieldsModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_comments")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
    )
    content = models.TextField()
    moderation_status = models.CharField(
        max_length=20,
        choices=ModerationStatusChoices.choices,
        default=ModerationStatusChoices.APPROVED,
        db_index=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment by {self.user}"


class Reaction(TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_reactions")
    reaction_type = models.CharField(max_length=10, choices=ReactionType.choices, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_post_reaction"),
        ]


class Report(AuditFieldsModel):
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="content_reports",
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reports", null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reports", null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING,
        db_index=True,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_reports",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if bool(self.post) == bool(self.comment):
            raise ValidationError("A report must target either a post or a comment.")

# Create your models here.
