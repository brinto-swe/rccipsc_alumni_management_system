"""Serializers for posts and related resources."""

from rest_framework import serializers

from common.serializers import CloudinaryImageSerializerField
from common.validators import validate_image_upload
from posts.models import Comment, Post, PostMedia, Reaction, Report
from users.serializers import UserSummarySerializer


class PostMediaSerializer(serializers.ModelSerializer):
    image = CloudinaryImageSerializerField(validators=[validate_image_upload])

    class Meta:
        model = PostMedia
        fields = ["id", "image", "caption", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class CommentSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "user",
            "parent",
            "content",
            "moderation_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "moderation_status", "created_at", "updated_at"]


class ReactionSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ["id", "post", "user", "reaction_type", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]


class ReportSerializer(serializers.ModelSerializer):
    reporter = UserSummarySerializer(read_only=True)
    reviewed_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "reporter",
            "post",
            "comment",
            "reason",
            "status",
            "reviewed_by",
            "reviewed_at",
            "resolution_note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["reporter", "status", "reviewed_by", "reviewed_at", "created_at", "updated_at"]


class ReportReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["in_review", "resolved", "dismissed"])
    resolution_note = serializers.CharField(required=False, allow_blank=True)


class PostSerializer(serializers.ModelSerializer):
    author = UserSummarySerializer(read_only=True)
    media_items = PostMediaSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    dislikes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "visibility",
            "moderation_status",
            "is_published",
            "is_comments_enabled",
            "published_at",
            "media_items",
            "comments_count",
            "likes_count",
            "dislikes_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "author",
            "moderation_status",
            "comments_count",
            "likes_count",
            "dislikes_count",
            "created_at",
            "updated_at",
        ]


class PostWriteSerializer(serializers.ModelSerializer):
    media_items = PostMediaSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ["content", "visibility", "is_published", "is_comments_enabled", "media_items"]
