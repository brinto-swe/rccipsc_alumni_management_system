"""Serializers for event APIs."""

from rest_framework import serializers

from common.serializers import CloudinaryFileSerializerField, CloudinaryImageSerializerField
from common.validators import validate_document_upload, validate_image_upload
from events.enums import EventType, PaymentMethod, PaymentStatus
from events.models import Event, EventGallery, EventRegistration, EventResult, EventReview, EventSponsor
from users.serializers import UserSummarySerializer


class EventSponsorSerializer(serializers.ModelSerializer):
    sponsor_logo = CloudinaryImageSerializerField(
        required=False,
        allow_null=True,
        validators=[validate_image_upload],
    )

    class Meta:
        model = EventSponsor
        fields = ["id", "event", "sponsor_name", "sponsor_logo", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class EventSponsorNestedSerializer(serializers.ModelSerializer):
    sponsor_logo = CloudinaryImageSerializerField(
        required=False,
        allow_null=True,
        validators=[validate_image_upload],
    )

    class Meta:
        model = EventSponsor
        fields = ["sponsor_name", "sponsor_logo"]


class EventGallerySerializer(serializers.ModelSerializer):
    image = CloudinaryImageSerializerField(validators=[validate_image_upload])
    uploaded_by = UserSummarySerializer(source="created_by", read_only=True)

    class Meta:
        model = EventGallery
        fields = [
            "id",
            "event",
            "image",
            "caption",
            "is_public",
            "display_order",
            "uploaded_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "uploaded_by"]


class EventResultSerializer(serializers.ModelSerializer):
    attachment = CloudinaryFileSerializerField(
        required=False,
        allow_null=True,
        validators=[validate_document_upload],
    )

    class Meta:
        model = EventResult
        fields = [
            "id",
            "event",
            "result_summary",
            "highlights",
            "post_event_information",
            "attachment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class EventReviewSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = EventReview
        fields = [
            "id",
            "event",
            "user",
            "rating",
            "comment",
            "moderation_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "moderation_status", "created_at", "updated_at"]


class EventRegistrationSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = EventRegistration
        fields = [
            "id",
            "event",
            "user",
            "status",
            "payment_status",
            "payment_reference",
            "note",
            "attendee_visibility",
            "ticket_code",
            "pdf_generated_at",
            "checked_in_at",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "status",
            "payment_status",
            "ticket_code",
            "pdf_generated_at",
            "checked_in_at",
            "created_at",
            "updated_at",
        ]


class EventRegistrationCreateSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True)
    attendee_visibility = serializers.ChoiceField(
        choices=EventRegistration._meta.get_field("attendee_visibility").choices,
        default="public",
    )


class EventListSerializer(serializers.ModelSerializer):
    banner = CloudinaryImageSerializerField(read_only=True)
    sponsors = EventSponsorSerializer(many=True, read_only=True)
    registration_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "event_type",
            "event_name",
            "slug",
            "banner",
            "batch",
            "season",
            "year",
            "event_date",
            "event_start_date",
            "event_end_date",
            "location",
            "registration_start_date",
            "registration_end_date",
            "payment_method",
            "status",
            "is_public",
            "registration_count",
            "sponsors",
        ]


class EventDetailSerializer(EventListSerializer):
    created_by = UserSummarySerializer(read_only=True)
    updated_by = UserSummarySerializer(read_only=True)
    gallery_items = EventGallerySerializer(many=True, read_only=True)
    result = EventResultSerializer(read_only=True)
    reviews = EventReviewSerializer(many=True, read_only=True)

    class Meta(EventListSerializer.Meta):
        fields = EventListSerializer.Meta.fields + [
            "invitation_letter",
            "gathering_time",
            "generate_registration_pdf",
            "generate_ticket_or_checkin_pdf",
            "creator_role",
            "participant_visibility",
            "metadata",
            "created_by",
            "updated_by",
            "gallery_items",
            "result",
            "reviews",
            "created_at",
            "updated_at",
        ]


class EventWriteSerializer(serializers.ModelSerializer):
    banner = CloudinaryImageSerializerField(
        required=False,
        allow_null=True,
        validators=[validate_image_upload],
    )
    sponsors = EventSponsorNestedSerializer(many=True, required=False)

    class Meta:
        model = Event
        exclude = ["created_by", "updated_by", "creator_role", "created_at", "updated_at"]

    def validate(self, attrs):
        event_type = attrs.get("event_type", getattr(self.instance, "event_type", None))
        user = self.context["request"].user

        if event_type == EventType.SPORTS_CARNIVAL and user.role != "admin":
            raise serializers.ValidationError("Only admins can create Sports Carnival events.")
        if event_type in {EventType.EFTAR_PARTY, EventType.REUNION, EventType.CUSTOM} and user.role not in {
            "admin",
            "staff",
        }:
            raise serializers.ValidationError("Only admin or staff can create this event type.")

        payment_method = attrs.get("payment_method", getattr(self.instance, "payment_method", PaymentMethod.NO_PAYMENT_REQUIRED))
        if payment_method == PaymentMethod.NO_PAYMENT_REQUIRED:
            attrs.setdefault("generate_registration_pdf", False)
        return attrs
