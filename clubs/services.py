"""Services for club management."""

from rest_framework.exceptions import PermissionDenied, ValidationError

from clubs.models import Club, ClubMembership


def create_club(*, actor, validated_data):
    if actor.role not in {"admin", "moderator"}:
        raise PermissionDenied("Only admins or moderators can create clubs.")
    return Club.objects.create(created_by=actor, updated_by=actor, **validated_data)


def update_club(*, actor, club: Club, validated_data):
    if actor.role not in {"admin", "moderator"}:
        raise PermissionDenied("Only admins or moderators can update clubs.")
    for field, value in validated_data.items():
        setattr(club, field, value)
    club.updated_by = actor
    club.save()
    return club


def join_club(*, actor, club: Club):
    if actor.role != "alumni":
        raise PermissionDenied("Only alumni can join clubs.")
    membership, created = ClubMembership.objects.get_or_create(
        club=club,
        user=actor,
        defaults={"status": "active"},
    )
    if not created and membership.status == "active":
        raise ValidationError("You are already a member of this club.")
    membership.status = "active"
    membership.save(update_fields=["status"])
    return membership


def leave_club(*, actor, membership: ClubMembership):
    if actor.role not in {"admin", "moderator"} and membership.user_id != actor.id:
        raise PermissionDenied("You may only leave your own club memberships.")
    membership.delete()
