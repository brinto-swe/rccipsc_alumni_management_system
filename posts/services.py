"""Services for feed mutations and moderation workflows."""

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from posts.enums import ReportStatus
from posts.models import Comment, Post, PostMedia, Reaction, Report


def _can_publish_post(actor):
    return actor.role in {"admin", "moderator", "alumni"}


@transaction.atomic
def create_post(*, actor, validated_data):
    if not _can_publish_post(actor):
        raise PermissionDenied("Only alumni, moderators, and admins can create posts.")
    media_items = validated_data.pop("media_items", [])
    post = Post.objects.create(author=actor, created_by=actor, updated_by=actor, **validated_data)
    for media in media_items:
        PostMedia.objects.create(post=post, created_by=actor, updated_by=actor, **media)
    return post


@transaction.atomic
def update_post(*, actor, post: Post, validated_data):
    if actor.role not in {"admin", "moderator"} and post.author_id != actor.id:
        raise PermissionDenied("You may only edit your own posts.")
    media_items = validated_data.pop("media_items", None)
    for field, value in validated_data.items():
        setattr(post, field, value)
    post.updated_by = actor
    post.save()
    if media_items is not None:
        post.media_items.all().delete()
        for media in media_items:
            PostMedia.objects.create(post=post, created_by=actor, updated_by=actor, **media)
    return post


def soft_delete_post(*, actor, post: Post):
    if actor.role not in {"admin", "moderator"} and post.author_id != actor.id:
        raise PermissionDenied("You may only delete your own posts.")
    post.soft_delete()


def create_comment(*, actor, validated_data):
    post = validated_data["post"]
    if not post.is_comments_enabled:
        raise ValidationError("Comments are disabled for this post.")
    return Comment.objects.create(user=actor, created_by=actor, updated_by=actor, **validated_data)


def update_comment(*, actor, comment: Comment, validated_data):
    if actor.role not in {"admin", "moderator"} and comment.user_id != actor.id:
        raise PermissionDenied("You may only edit your own comments.")
    for field, value in validated_data.items():
        setattr(comment, field, value)
    comment.updated_by = actor
    comment.save()
    return comment


def soft_delete_comment(*, actor, comment: Comment):
    if actor.role not in {"admin", "moderator"} and comment.user_id != actor.id:
        raise PermissionDenied("You may only delete your own comments.")
    comment.soft_delete()


def set_reaction(*, actor, validated_data):
    reaction, _ = Reaction.objects.update_or_create(
        user=actor,
        post=validated_data["post"],
        defaults={"reaction_type": validated_data["reaction_type"]},
    )
    return reaction


def create_report(*, actor, validated_data):
    return Report.objects.create(reporter=actor, created_by=actor, updated_by=actor, **validated_data)


def review_report(*, actor, report: Report, status: str, resolution_note: str = ""):
    if actor.role not in {"admin", "moderator"}:
        raise PermissionDenied("Only moderators and admins may review reports.")
    report.status = status
    report.reviewed_by = actor
    report.reviewed_at = timezone.now()
    report.resolution_note = resolution_note
    report.updated_by = actor
    report.save()

    if status == ReportStatus.RESOLVED:
        if report.post:
            report.post.moderation_status = "removed"
            report.post.save(update_fields=["moderation_status", "updated_at"])
        if report.comment:
            report.comment.moderation_status = "removed"
            report.comment.save(update_fields=["moderation_status", "updated_at"])

    return report
