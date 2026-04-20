"""Serializers for mentorship APIs."""

from rest_framework import serializers

from mentorships.models import MentorProfile, MentorshipFeedback, MentorshipRequest, MentorshipSession
from users.serializers import UserSummarySerializer


class MentorProfileSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = MentorProfile
        fields = [
            "id",
            "user",
            "professional_title",
            "expertise_areas",
            "bio",
            "status",
            "approval_note",
            "approved_by",
            "approved_at",
            "is_accepting_mentees",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "status", "approval_note", "approved_by", "approved_at", "created_at", "updated_at"]


class MentorProfileReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["approved", "rejected"])
    approval_note = serializers.CharField(required=False, allow_blank=True)


class MentorshipRequestSerializer(serializers.ModelSerializer):
    mentee = UserSummarySerializer(read_only=True)

    class Meta:
        model = MentorshipRequest
        fields = [
            "id",
            "mentor_profile",
            "mentee",
            "message",
            "status",
            "response_note",
            "responded_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["mentee", "status", "response_note", "responded_at", "created_at", "updated_at"]


class MentorshipRequestResponseSerializer(serializers.Serializer):
    response_note = serializers.CharField(required=False, allow_blank=True)


class MentorshipSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorshipSession
        fields = [
            "id",
            "mentorship_request",
            "scheduled_at",
            "duration_minutes",
            "meeting_link",
            "location",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class MentorshipFeedbackSerializer(serializers.ModelSerializer):
    author = UserSummarySerializer(read_only=True)

    class Meta:
        model = MentorshipFeedback
        fields = ["id", "session", "author", "rating", "comment", "created_at", "updated_at"]
        read_only_fields = ["author", "created_at", "updated_at"]
