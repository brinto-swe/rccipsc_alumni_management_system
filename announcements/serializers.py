"""Serializers for announcements and categories."""

from rest_framework import serializers

from announcements.models import Announcement, AnnouncementCategory


class AnnouncementCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementCategory
        fields = ["id", "name", "slug", "description", "created_at", "updated_at"]
        read_only_fields = ["slug", "created_at", "updated_at"]


class AnnouncementSerializer(serializers.ModelSerializer):
    category_detail = AnnouncementCategorySerializer(source="category", read_only=True)

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "category",
            "category_detail",
            "is_pinned",
            "is_published",
            "visibility",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "published_at", "created_at", "updated_at"]
