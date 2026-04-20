"""Profile-domain services."""

from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from profiles.enums import VerificationRequestStatus
from profiles.models import AlumniProfile, AlumniVerificationRequest
from users.enums import UserRole


def update_profile(*, actor, profile: AlumniProfile, validated_data: dict) -> AlumniProfile:
    if actor != profile.user and actor.role != UserRole.ADMIN:
        raise PermissionDenied("You can only update your own profile.")

    for field, value in validated_data.items():
        setattr(profile, field, value)
    profile.updated_by = actor
    profile.save()
    return profile


def create_verification_request(*, actor, note: str = "") -> AlumniVerificationRequest:
    if actor.role != UserRole.ALUMNI:
        raise PermissionDenied("Only alumni may request verification.")
    if actor.is_verified:
        raise ValidationError("Your account is already verified.")
    if AlumniVerificationRequest.objects.filter(
        user=actor,
        status=VerificationRequestStatus.PENDING,
    ).exists():
        raise ValidationError("You already have a pending verification request.")

    return AlumniVerificationRequest.objects.create(user=actor, note=note)


def review_verification_request(*, actor, verification_request: AlumniVerificationRequest, status: str, review_note: str = ""):
    if actor.role not in {UserRole.ADMIN, UserRole.MODERATOR}:
        raise PermissionDenied("Only admin or moderators may review verification requests.")

    verification_request.status = status
    verification_request.review_note = review_note
    verification_request.reviewed_by = actor
    verification_request.reviewed_at = timezone.now()
    verification_request.save()

    if status == VerificationRequestStatus.APPROVED:
        verification_request.user.is_verified = True
        verification_request.user.save(update_fields=["is_verified", "updated_at"])

    return verification_request
