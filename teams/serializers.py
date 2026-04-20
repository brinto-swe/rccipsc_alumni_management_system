"""Serializers for team workflows."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from teams.models import Team, TeamEventRegistration, TeamMember
from users.serializers import UserSummarySerializer


User = get_user_model()


class TeamSerializer(serializers.ModelSerializer):
    captain = UserSummarySerializer(read_only=True)
    captain_id = serializers.PrimaryKeyRelatedField(
        source="captain",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    members_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "sport_type",
            "batch_year",
            "description",
            "captain",
            "captain_id",
            "is_active",
            "members_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "members_count"]


class TeamMemberSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(source="user", queryset=User.objects.all(), write_only=True)

    class Meta:
        model = TeamMember
        fields = ["id", "team", "user", "user_id", "role", "is_active", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]


class TeamEventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamEventRegistration
        fields = ["id", "team", "event", "status", "note", "created_at", "updated_at"]
        read_only_fields = ["status", "created_at", "updated_at"]
