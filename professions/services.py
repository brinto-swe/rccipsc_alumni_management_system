"""Profession-domain services."""

from rest_framework.exceptions import PermissionDenied

from professions.models import Profession
from users.enums import UserRole


def create_profession(*, actor, profile, validated_data):
    if actor != profile.user and actor.role != UserRole.ADMIN:
        raise PermissionDenied("You may only add professions to your own profile.")
    return Profession.objects.create(
        profile=profile,
        created_by=actor,
        updated_by=actor,
        **validated_data,
    )


def update_profession(*, actor, profession: Profession, validated_data):
    if actor != profession.profile.user and actor.role != UserRole.ADMIN:
        raise PermissionDenied("You may only update your own profession entries.")
    for field, value in validated_data.items():
        setattr(profession, field, value)
    profession.updated_by = actor
    profession.save()
    return profession


def delete_profession(*, actor, profession: Profession):
    if actor != profession.profile.user and actor.role != UserRole.ADMIN:
        raise PermissionDenied("You may only delete your own profession entries.")
    profession.delete()
