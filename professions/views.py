"""Profession API views."""

from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from professions.selectors import get_profession_queryset
from professions.serializers import ProfessionSerializer
from professions.services import create_profession, delete_profession, update_profession


@extend_schema_view(
    list=extend_schema(tags=["Profiles"]),
    create=extend_schema(tags=["Profiles"]),
    retrieve=extend_schema(tags=["Profiles"]),
    partial_update=extend_schema(tags=["Profiles"]),
    destroy=extend_schema(tags=["Profiles"]),
)
class ProfessionViewSet(viewsets.ModelViewSet):
    serializer_class = ProfessionSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["present_occupation", "role", "institution_or_organization_name"]
    ordering_fields = ["starting_date", "ending_date", "created_at"]

    def get_queryset(self):
        return get_profession_queryset(self.request.user)

    def perform_create(self, serializer):
        create_profession(
            actor=self.request.user,
            profile=self.request.user.profile,
            validated_data=serializer.validated_data,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profession = create_profession(
            actor=request.user,
            profile=request.user.profile,
            validated_data=serializer.validated_data,
        )
        output = self.get_serializer(profession)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        update_profession(
            actor=self.request.user,
            profession=self.get_object(),
            validated_data=serializer.validated_data,
        )

    def perform_destroy(self, instance):
        delete_profession(actor=self.request.user, profession=instance)
