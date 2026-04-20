"""Club API views."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from clubs.permissions import CanReadClubs
from clubs.selectors import get_club_membership_queryset, get_visible_clubs
from clubs.serializers import ClubMembershipSerializer, ClubSerializer
from clubs.services import create_club, join_club, leave_club, update_club


@extend_schema_view(
    list=extend_schema(tags=["Clubs"]),
    retrieve=extend_schema(tags=["Clubs"]),
    create=extend_schema(tags=["Clubs"]),
    partial_update=extend_schema(tags=["Clubs"]),
)
class ClubViewSet(viewsets.ModelViewSet):
    serializer_class = ClubSerializer
    permission_classes = [CanReadClubs]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    filterset_fields = ["visibility", "is_active"]

    def get_queryset(self):
        return get_visible_clubs(self.request.user)

    def get_permissions(self):
        if self.action in {"create", "partial_update", "join", "destroy"}:
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        club = create_club(actor=request.user, validated_data=serializer.validated_data)
        return Response(ClubSerializer(club, context={"request": request}).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        club = self.get_object()
        serializer = self.get_serializer(club, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        club = update_club(actor=request.user, club=club, validated_data=serializer.validated_data)
        return Response(ClubSerializer(club, context={"request": request}).data)

    def destroy(self, request, *args, **kwargs):
        club = self.get_object()
        if request.user.role not in {"admin", "moderator"}:
            return Response({"detail": "Only admins or moderators can delete clubs."}, status=status.HTTP_403_FORBIDDEN)
        club.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(tags=["Clubs"], responses=ClubMembershipSerializer)
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def join(self, request, *args, **kwargs):
        membership = join_club(actor=request.user, club=self.get_object())
        return Response(ClubMembershipSerializer(membership, context={"request": request}).data)


@extend_schema_view(
    list=extend_schema(tags=["Clubs"]),
    destroy=extend_schema(tags=["Clubs"]),
)
class ClubMembershipViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = ClubMembershipSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["club", "status", "membership_role"]

    def get_queryset(self):
        return get_club_membership_queryset(self.request.user)

    def destroy(self, request, *args, **kwargs):
        membership = self.get_object()
        leave_club(actor=request.user, membership=membership)
        return Response(status=status.HTTP_204_NO_CONTENT)
