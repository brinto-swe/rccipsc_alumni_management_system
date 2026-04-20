"""Directory API views."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from directory.filters import AlumniDirectoryFilterSet
from directory.permissions import CanBrowseDirectory
from directory.selectors import get_directory_queryset, get_suggested_alumni_queryset
from directory.serializers import DirectoryProfileSerializer


@extend_schema_view(
    list=extend_schema(tags=["Directory"]),
    retrieve=extend_schema(tags=["Directory"]),
)
class AlumniDirectoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = DirectoryProfileSerializer
    permission_classes = [CanBrowseDirectory]
    filterset_class = AlumniDirectoryFilterSet
    search_fields = [
        "full_name",
        "student_id",
        "class_roll",
        "current_city",
        "current_country",
        "professions__present_occupation",
        "professions__role",
        "professions__institution_or_organization_name",
    ]
    ordering_fields = ["full_name", "batch_year", "current_city", "created_at"]

    def get_queryset(self):
        return get_directory_queryset(self.request.user)

    @extend_schema(tags=["Directory"], responses=DirectoryProfileSerializer(many=True))
    @action(detail=False, methods=["get"])
    def suggested(self, request, *args, **kwargs):
        queryset = get_suggested_alumni_queryset(request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
