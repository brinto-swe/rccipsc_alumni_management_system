"""Serializers for user-related APIs."""

from rest_framework import serializers

from users.enums import AccountStatus, UserRole
from users.models import User


class UserSummarySerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "full_name",
            "role",
            "account_status",
            "is_active",
            "is_verified",
            "managed_batch_year",
        ]

    def get_full_name(self, obj):
        if hasattr(obj, "profile") and obj.profile.full_name:
            return obj.profile.full_name
        return obj.username or obj.email


class UserDetailSerializer(UserSummarySerializer):
    class Meta(UserSummarySerializer.Meta):
        fields = UserSummarySerializer.Meta.fields + [
            "date_joined",
            "last_login",
        ]


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "role",
            "account_status",
            "is_active",
            "is_verified",
            "managed_batch_year",
            "username",
        ]

    def validate_role(self, value):
        if value == UserRole.ADMIN and not self.context["request"].user.is_superuser:
            raise serializers.ValidationError("Only superusers may promote another user to admin.")
        return value

    def validate(self, attrs):
        role = attrs.get("role", self.instance.role)
        managed_batch_year = attrs.get("managed_batch_year", self.instance.managed_batch_year)
        if role == UserRole.STAFF and not managed_batch_year:
            raise serializers.ValidationError(
                {"managed_batch_year": "Batch staff must have an assigned managed batch year."}
            )
        if role != UserRole.STAFF:
            attrs["managed_batch_year"] = None
        return attrs
