"""Serializers for club workflows."""

from rest_framework import serializers

from clubs.models import Club, ClubMembership
from users.serializers import UserSummarySerializer


class ClubMembershipSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = ClubMembership
        fields = ["id", "club", "user", "membership_role", "status", "joined_at", "created_at", "updated_at"]
        read_only_fields = ["user", "joined_at", "created_at", "updated_at"]


class ClubSerializer(serializers.ModelSerializer):
    memberships_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Club
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "visibility",
            "is_active",
            "memberships_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "memberships_count", "created_at", "updated_at"]
