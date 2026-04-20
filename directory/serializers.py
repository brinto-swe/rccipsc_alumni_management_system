"""Serializers for directory APIs."""

from rest_framework import serializers

from profiles.models import AlumniProfile


class DirectoryProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    latest_profession = serializers.SerializerMethodField()
    is_verified = serializers.BooleanField(source="user.is_verified", read_only=True)

    class Meta:
        model = AlumniProfile
        fields = [
            "id",
            "full_name",
            "batch_year",
            "academic_group",
            "bio",
            "profile_picture",
            "current_city",
            "current_country",
            "email",
            "phone_number",
            "latest_profession",
            "is_verified",
            "directory_visibility",
        ]

    def _can_view(self, obj, visibility):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if visibility == "public":
            return True
        if not user or not user.is_authenticated:
            return False
        if obj.user == user or user.role in {"admin", "moderator"}:
            return True
        return visibility == "alumni_only" and user.role in {"alumni", "staff", "admin", "moderator"}

    def get_email(self, obj):
        if self._can_view(obj, obj.email_visibility):
            return obj.user.email
        return None

    def get_phone_number(self, obj):
        if self._can_view(obj, obj.phone_visibility):
            return obj.phone_number
        return None

    def get_latest_profession(self, obj):
        profession = obj.professions.first()
        if not profession:
            return None
        return {
            "present_occupation": profession.present_occupation,
            "role": profession.role,
            "institution_or_organization_name": profession.institution_or_organization_name,
            "currently_working_here": profession.currently_working_here,
        }
