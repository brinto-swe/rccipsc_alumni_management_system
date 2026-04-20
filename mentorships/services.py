"""Services for mentorship lifecycle operations."""

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from mentorships.enums import MentorProfileStatus, MentorshipRequestStatus
from mentorships.models import MentorProfile, MentorshipFeedback, MentorshipRequest, MentorshipSession


def apply_as_mentor(*, actor, validated_data):
    if actor.role != "alumni":
        raise PermissionDenied("Only alumni can apply to become mentors.")
    mentor_profile, created = MentorProfile.objects.update_or_create(
        user=actor,
        defaults={
            **validated_data,
            "status": MentorProfileStatus.PENDING,
            "created_by": actor,
            "updated_by": actor,
        },
    )
    return mentor_profile


def review_mentor_profile(*, actor, mentor_profile: MentorProfile, status: str, approval_note: str = ""):
    if actor.role != "admin":
        raise PermissionDenied("Only admins can review mentor applications.")
    mentor_profile.status = status
    mentor_profile.approval_note = approval_note
    mentor_profile.approved_by = actor
    mentor_profile.approved_at = timezone.now()
    mentor_profile.updated_by = actor
    mentor_profile.save()
    return mentor_profile


def create_mentorship_request(*, actor, validated_data):
    mentor_profile = validated_data["mentor_profile"]
    if mentor_profile.status != MentorProfileStatus.APPROVED:
        raise ValidationError("This mentor is not currently approved.")
    request = MentorshipRequest.objects.create(
        mentee=actor,
        created_by=actor,
        updated_by=actor,
        **validated_data,
    )
    try:
        from notifications.services import create_notification

        create_notification(
            recipient=mentor_profile.user,
            title="New mentorship request",
            message="A mentee has requested mentorship from you.",
            notification_type="mentorship_update",
            action_url=f"/mentorship/requests/{request.id}",
            metadata={"request_id": str(request.id)},
        )
    except Exception:
        pass
    return request


def respond_to_request(*, actor, mentorship_request: MentorshipRequest, status: str, response_note: str = ""):
    if mentorship_request.mentor_profile.user_id != actor.id:
        raise PermissionDenied("Only the mentor can respond to this request.")
    mentorship_request.status = status
    mentorship_request.response_note = response_note
    mentorship_request.responded_at = timezone.now()
    mentorship_request.updated_by = actor
    mentorship_request.save()
    try:
        from notifications.services import create_notification

        create_notification(
            recipient=mentorship_request.mentee,
            title=f"Mentorship request {status}",
            message=response_note or "Your mentorship request status has changed.",
            notification_type="mentorship_update",
            action_url=f"/mentorship/requests/{mentorship_request.id}",
            metadata={"request_id": str(mentorship_request.id), "status": status},
        )
    except Exception:
        pass
    return mentorship_request


def schedule_session(*, actor, validated_data):
    mentorship_request = validated_data["mentorship_request"]
    if actor.id not in {mentorship_request.mentee_id, mentorship_request.mentor_profile.user_id} and actor.role != "admin":
        raise PermissionDenied("Only session participants or admins can schedule sessions.")
    if mentorship_request.status != MentorshipRequestStatus.ACCEPTED:
        raise ValidationError("Sessions can only be scheduled for accepted mentorship requests.")
    session = MentorshipSession.objects.create(created_by=actor, updated_by=actor, **validated_data)
    try:
        from notifications.services import create_notification

        for recipient in [mentorship_request.mentee, mentorship_request.mentor_profile.user]:
            create_notification(
                recipient=recipient,
                title="Mentorship session scheduled",
                message="A mentorship session has been scheduled.",
                notification_type="mentorship_update",
                action_url=f"/mentorship/sessions/{session.id}",
                metadata={"session_id": str(session.id)},
            )
    except Exception:
        pass
    return session


def submit_feedback(*, actor, validated_data):
    session = validated_data["session"]
    if actor.id not in {
        session.mentorship_request.mentee_id,
        session.mentorship_request.mentor_profile.user_id,
    }:
        raise PermissionDenied("Only session participants may leave feedback.")
    return MentorshipFeedback.objects.create(author=actor, **validated_data)
