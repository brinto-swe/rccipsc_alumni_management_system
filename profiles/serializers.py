"""Serializers for profile APIs."""

from rest_framework import serializers

from common.enums import VisibilityChoices
from common.serializers import CloudinaryImageSerializerField
from common.validators import validate_image_upload
from professions.serializers import ProfessionSerializer
from profiles.enums import VerificationRequestStatus
from profiles.models import AlumniProfile, AlumniVerificationRequest
from users.serializers import UserSummarySerializer


class AlumniProfileSerializer(serializers.ModelSerializer):
    profile_picture = CloudinaryImageSerializerField(read_only=True)
    user = UserSummarySerializer(read_only=True)
    professions = ProfessionSerializer(many=True, read_only=True)
    email = serializers.SerializerMethodField()
    social_links = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()

    class Meta:
        model = AlumniProfile
        fields = [
            "id",
            "user",
            "full_name",
            "student_id",
            "class_roll",
            "batch_year",
            "academic_group",
            "ssc_passing_year",
            "ssc_school_name",
            "hsc_passing_year",
            "hsc_school_name",
            "bio",
            "profile_picture",
            "phone_number",
            "present_address",
            "permanent_address",
            "current_city",
            "current_country",
            "email",
            "social_links",
            "directory_visibility",
            "email_visibility",
            "phone_visibility",
            "social_link_visibility",
            "professions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def _can_view(self, visibility, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if visibility == VisibilityChoices.PUBLIC:
            return True
        if not user or not user.is_authenticated:
            return False
        if obj.user == user or user.role in {"admin", "moderator"}:
            return True
        return visibility == VisibilityChoices.ALUMNI_ONLY and user.role in {"alumni", "staff", "admin", "moderator"}

    def get_email(self, obj):
        if self._can_view(obj.email_visibility, obj):
            return obj.user.email
        return None

    def get_phone_number(self, obj):
        if self._can_view(obj.phone_visibility, obj):
            return obj.phone_number
        return None

    def get_social_links(self, obj):
        if self._can_view(obj.social_link_visibility, obj):
            return obj.social_links
        return {}


class AlumniProfileUpdateSerializer(serializers.ModelSerializer):
    profile_picture = CloudinaryImageSerializerField(
        required=False,
        allow_null=True,
        validators=[validate_image_upload],
    )

    class Meta:
        model = AlumniProfile
        exclude = ["user", "created_by", "updated_by", "created_at", "updated_at"]


class AlumniVerificationRequestSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = AlumniVerificationRequest
        fields = [
            "id",
            "user",
            "status",
            "note",
            "review_note",
            "reviewed_by",
            "reviewed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "status",
            "review_note",
            "reviewed_by",
            "reviewed_at",
            "created_at",
            "updated_at",
        ]


class AlumniVerificationReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            VerificationRequestStatus.APPROVED,
            VerificationRequestStatus.REJECTED,
        ]
    )
    review_note = serializers.CharField(required=False, allow_blank=True)
