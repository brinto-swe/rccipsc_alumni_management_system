"""Services for batch-scoped team operations."""

from rest_framework.exceptions import PermissionDenied

from teams.models import Team, TeamEventRegistration, TeamMember


def _assert_team_manager(actor, batch_year=None):
    if actor.role == "admin":
        return
    if actor.role != "staff":
        raise PermissionDenied("Only batch staff or admins can manage teams.")
    if batch_year and actor.managed_batch_year != batch_year:
        raise PermissionDenied("Staff can only manage teams for their own batch.")


def create_team(*, actor, validated_data):
    _assert_team_manager(actor, validated_data["batch_year"])
    team = Team.objects.create(created_by=actor, updated_by=actor, **validated_data)
    if team.captain:
        TeamMember.objects.get_or_create(team=team, user=team.captain, defaults={"role": "captain"})
    return team


def update_team(*, actor, team: Team, validated_data):
    _assert_team_manager(actor, team.batch_year)
    if actor.role == "staff" and team.created_by_id != actor.id:
        raise PermissionDenied("Staff can only manage teams they created.")
    for field, value in validated_data.items():
        setattr(team, field, value)
    team.updated_by = actor
    team.save()
    return team


def add_team_member(*, actor, validated_data):
    team = validated_data["team"]
    _assert_team_manager(actor, team.batch_year)
    if actor.role == "staff" and team.created_by_id != actor.id:
        raise PermissionDenied("Staff can only manage members for their own teams.")
    return TeamMember.objects.create(**validated_data)


def remove_team_member(*, actor, team_member: TeamMember):
    _assert_team_manager(actor, team_member.team.batch_year)
    if actor.role == "staff" and team_member.team.created_by_id != actor.id:
        raise PermissionDenied("Staff can only manage members for their own teams.")
    team_member.delete()


def register_team_for_event(*, actor, validated_data):
    team = validated_data["team"]
    event = validated_data["event"]
    _assert_team_manager(actor, team.batch_year)
    if actor.role == "staff" and team.created_by_id != actor.id:
        raise PermissionDenied("Staff can only register their own teams.")
    if event.event_type not in {"sports_carnival", "custom_event"}:
        raise PermissionDenied("Teams can only register for Sports Carnival or Custom events.")
    return TeamEventRegistration.objects.create(
        created_by=actor,
        updated_by=actor,
        **validated_data,
    )
