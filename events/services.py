"""Services for event lifecycle management."""

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from common.utils import generate_slug
from events.enums import EventType, PaymentMethod, PaymentStatus, RegistrationStatus
from events.models import Event, EventGallery, EventRegistration, EventResult, EventReview, EventSponsor
from events.validators import validate_registration_window_open


def _unique_event_slug(name: str) -> str:
    base_slug = generate_slug(name)
    slug = base_slug
    counter = 1
    while Event.objects.filter(slug=slug).exists():
        counter += 1
        slug = f"{base_slug}-{counter}"
    return slug


def _assert_event_write_permission(actor, event_type: str):
    if event_type == EventType.SPORTS_CARNIVAL and actor.role != "admin":
        raise PermissionDenied("Only admins can create Sports Carnival events.")
    if event_type in {EventType.EFTAR_PARTY, EventType.REUNION, EventType.CUSTOM} and actor.role not in {
        "admin",
        "staff",
    }:
        raise PermissionDenied("Only admin or staff can create this event type.")


def _assert_event_manage_permission(actor, event: Event):
    if actor.role == "admin":
        return
    if event.created_by_id != actor.id:
        raise PermissionDenied("You can only manage events you created.")


@transaction.atomic
def create_event(*, actor, validated_data: dict) -> Event:
    sponsors = validated_data.pop("sponsors", [])
    event_type = validated_data["event_type"]
    _assert_event_write_permission(actor, event_type)

    validated_data["slug"] = _unique_event_slug(validated_data["event_name"])
    validated_data["created_by"] = actor
    validated_data["updated_by"] = actor
    validated_data["creator_role"] = actor.role
    event = Event(**validated_data)
    event.full_clean()
    event.save()
    for sponsor in sponsors:
        EventSponsor.objects.create(
            event=event,
            created_by=actor,
            updated_by=actor,
            **sponsor,
        )
    return event


@transaction.atomic
def update_event(*, actor, event: Event, validated_data: dict) -> Event:
    sponsors = validated_data.pop("sponsors", None)
    _assert_event_manage_permission(actor, event)
    if "event_name" in validated_data and validated_data["event_name"] != event.event_name:
        validated_data["slug"] = _unique_event_slug(validated_data["event_name"])

    for field, value in validated_data.items():
        setattr(event, field, value)
    event.updated_by = actor
    event.full_clean()
    event.save()

    if sponsors is not None:
        event.sponsors.all().delete()
        for sponsor in sponsors:
            EventSponsor.objects.create(
                event=event,
                created_by=actor,
                updated_by=actor,
                **sponsor,
            )
    return event


def delete_event(*, actor, event: Event):
    _assert_event_manage_permission(actor, event)
    event.delete()


@transaction.atomic
def register_for_event(*, actor, event: Event, note: str = "", attendee_visibility: str = "public") -> EventRegistration:
    if not actor.is_authenticated:
        raise PermissionDenied("Authentication is required to register for events.")
    validate_registration_window_open(event)
    if EventRegistration.objects.filter(event=event, user=actor).exists():
        raise ValidationError("You have already registered for this event.")

    payment_status = (
        PaymentStatus.NOT_REQUIRED
        if event.payment_method == PaymentMethod.NO_PAYMENT_REQUIRED
        else PaymentStatus.PENDING
    )
    registration = EventRegistration.objects.create(
        event=event,
        user=actor,
        status=RegistrationStatus.CONFIRMED
        if payment_status == PaymentStatus.NOT_REQUIRED
        else RegistrationStatus.PENDING,
        payment_status=payment_status,
        note=note,
        attendee_visibility=attendee_visibility,
        ticket_code=f"EVT-{timezone.now().strftime('%Y%m%d%H%M%S')}",
    )
    if event.generate_registration_pdf or event.generate_ticket_or_checkin_pdf:
        registration.pdf_generated_at = timezone.now()
        registration.save(update_fields=["pdf_generated_at"])

    try:
        from notifications.services import create_notification, queue_email_message

        create_notification(
            recipient=actor,
            title=f"Registered for {event.event_name}",
            message="Your registration has been received.",
            notification_type="event_registration",
            action_url=f"/events/{event.slug}",
            metadata={"event_id": str(event.id)},
        )
        queue_email_message(
            recipient=actor,
            subject=f"Registration received: {event.event_name}",
            body="Your event registration has been recorded.",
            metadata={"event_id": str(event.id)},
        )
    except Exception:
        pass

    return registration


def add_gallery_item(*, actor, event: Event, validated_data: dict) -> EventGallery:
    _assert_event_manage_permission(actor, event)
    if not event.has_ended() and actor.role != "admin":
        raise ValidationError("Gallery uploads are only available after the event ends.")
    return EventGallery.objects.create(
        event=event,
        created_by=actor,
        updated_by=actor,
        **validated_data,
    )


def upsert_event_result(*, actor, event: Event, validated_data: dict) -> EventResult:
    _assert_event_manage_permission(actor, event)
    if not event.has_ended() and actor.role != "admin":
        raise ValidationError("Results can only be published after the event ends.")
    result, _ = EventResult.objects.update_or_create(
        event=event,
        defaults={
            **validated_data,
            "created_by": actor,
            "updated_by": actor,
        },
    )
    return result


def create_event_review(*, actor, event: Event, validated_data: dict) -> EventReview:
    if not event.has_ended():
        raise ValidationError("Reviews can only be submitted after the event ends.")
    review, created = EventReview.objects.update_or_create(
        event=event,
        user=actor,
        defaults={
            **validated_data,
            "created_by": actor,
            "updated_by": actor,
        },
    )
    return review
