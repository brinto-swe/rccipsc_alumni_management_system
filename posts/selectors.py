"""Selectors for post feeds and moderation views."""

from django.db.models import Count, Q

from posts.enums import PostVisibility
from posts.models import Comment, Post, Reaction, Report


def get_visible_post_queryset(user):
    queryset = (
        Post.objects.filter(is_deleted=False, is_published=True, moderation_status="approved")
        .select_related("author")
        .prefetch_related("media_items")
        .annotate(
            comments_count=Count("comments", filter=Q(comments__is_deleted=False), distinct=True),
            likes_count=Count("reactions", filter=Q(reactions__reaction_type="like"), distinct=True),
            dislikes_count=Count("reactions", filter=Q(reactions__reaction_type="dislike"), distinct=True),
        )
    )
    if not user or not user.is_authenticated:
        return queryset.filter(visibility=PostVisibility.PUBLIC)
    if user.role in {"admin", "moderator", "staff", "alumni"}:
        return queryset.filter(
            Q(visibility=PostVisibility.PUBLIC)
            | Q(visibility=PostVisibility.AUTHENTICATED)
            | Q(visibility=PostVisibility.ALUMNI_ONLY)
            | Q(author=user)
        ).distinct()
    return queryset.filter(Q(visibility=PostVisibility.PUBLIC) | Q(visibility=PostVisibility.AUTHENTICATED) | Q(author=user)).distinct()


def get_comment_queryset(user):
    queryset = Comment.objects.filter(is_deleted=False, moderation_status="approved").select_related("user", "post")
    if not user or not user.is_authenticated:
        return queryset.filter(post__visibility=PostVisibility.PUBLIC)
    return queryset


def get_reaction_queryset(user):
    queryset = Reaction.objects.select_related("user", "post").order_by("-created_at")
    if not user or not user.is_authenticated:
        return queryset.none()
    if user.role in {"admin", "moderator"}:
        return queryset
    return queryset.filter(user=user)


def get_report_queryset(user):
    queryset = Report.objects.select_related("reporter", "reviewed_by", "post", "comment").order_by("-created_at")
    if not user or not user.is_authenticated:
        return queryset.none()
    if user.role in {"admin", "moderator"}:
        return queryset
    return queryset.filter(reporter=user)
