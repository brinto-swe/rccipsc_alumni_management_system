"""Validators for event workflows."""

from django.core.exceptions import ValidationError
from django.utils import timezone

from events.enums import EventType


def validate_event_dates(event):
    if event.event_start_date and event.event_end_date and event.event_end_date < event.event_start_date:
        raise ValidationError("Event end date must be after event start date.")
    if (
        event.registration_start_date
        and event.registration_end_date
        and event.registration_end_date < event.registration_start_date
    ):
        raise ValidationError("Registration end date must be after registration start date.")
    if event.registration_end_date and event.event_start_date and event.registration_end_date > event.event_start_date:
        raise ValidationError("Registration must close on or before the event start date.")


def validate_event_type_requirements(event):
    if event.event_type in {EventType.EFTAR_PARTY, EventType.REUNION}:
        if not event.batch:
            raise ValidationError("Batch is required for Eftar Party and Reunion events.")
        if not event.event_date:
            raise ValidationError("Event date is required for Eftar Party and Reunion events.")
    if event.event_type == EventType.SPORTS_CARNIVAL:
        required = {
            "season": event.season,
            "year": event.year,
            "event_start_date": event.event_start_date,
            "event_end_date": event.event_end_date,
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            missing_text = ", ".join(missing)
            raise ValidationError(f"Sports Carnival requires: {missing_text}.")


def validate_registration_window_open(event):
    now = timezone.now()
    if not event.registration_start_date or not event.registration_end_date:
        raise ValidationError("Registration dates are not configured for this event.")
    if event.registration_start_date > now:
        raise ValidationError("Registration has not opened yet.")
    if event.registration_end_date < now:
        raise ValidationError("Registration is closed for this event.")
