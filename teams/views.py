"""Team API views."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from teams.permissions import CanReadTeams
from teams.selectors import get_team_event_registration_queryset, get_team_member_queryset, get_team_queryset
from teams.serializers import TeamEventRegistrationSerializer, TeamMemberSerializer, TeamSerializer
from teams.services import add_team_member, create_team, register_team_for_event, remove_team_member, update_team


@extend_schema_view(
    list=extend_schema(tags=["Teams"]),
    retrieve=extend_schema(tags=["Teams"]),
    create=extend_schema(tags=["Teams"]),
    partial_update=extend_schema(tags=["Teams"]),
)
class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [CanReadTeams]
    search_fields = ["name", "sport_type", "description"]
    ordering_fields = ["name", "batch_year", "created_at"]
    filterset_fields = ["batch_year", "sport_type", "is_active"]

    def get_queryset(self):
        return get_team_queryset(self.request.user)

    def get_permissions(self):
        if self.action in {"create", "partial_update", "destroy"}:
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = create_team(actor=request.user, validated_data=serializer.validated_data)
        return Response(TeamSerializer(team, context={"request": request}).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        team = self.get_object()
        serializer = self.get_serializer(team, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        team = update_team(actor=request.user, team=team, validated_data=serializer.validated_data)
        return Response(TeamSerializer(team, context={"request": request}).data)

    def destroy(self, request, *args, **kwargs):
        team = self.get_object()
        update_team(actor=request.user, team=team, validated_data={"is_active": False})
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(tags=["Teams"]),
    create=extend_schema(tags=["Teams"]),
    destroy=extend_schema(tags=["Teams"]),
)
class TeamMemberViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["team", "role", "is_active"]

    def get_queryset(self):
        return get_team_member_queryset(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team_member = add_team_member(actor=request.user, validated_data=serializer.validated_data)
        return Response(TeamMemberSerializer(team_member, context={"request": request}).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        team_member = self.get_object()
        remove_team_member(actor=request.user, team_member=team_member)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(tags=["Teams"]),
    create=extend_schema(tags=["Teams"]),
)
class TeamEventRegistrationViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = TeamEventRegistrationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["team", "event", "status"]

    def get_queryset(self):
        return get_team_event_registration_queryset(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registration = register_team_for_event(actor=request.user, validated_data=serializer.validated_data)
        return Response(
            TeamEventRegistrationSerializer(registration, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
