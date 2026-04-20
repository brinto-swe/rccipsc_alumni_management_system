"""Announcement and news API views."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from announcements.permissions import CanReadAnnouncements
from announcements.selectors import get_announcement_categories, get_visible_announcements
from announcements.serializers import AnnouncementCategorySerializer, AnnouncementSerializer
from announcements.services import create_announcement, create_category, update_announcement


@extend_schema_view(
    list=extend_schema(tags=["Announcements"]),
    create=extend_schema(tags=["Announcements"]),
    retrieve=extend_schema(tags=["Announcements"]),
)
class AnnouncementCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementCategorySerializer
    permission_classes = [CanReadAnnouncements]
    http_method_names = ["get", "post"]

    def get_queryset(self):
        return get_announcement_categories()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = create_category(actor=request.user, validated_data=serializer.validated_data)
        return Response(AnnouncementCategorySerializer(category).data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(tags=["Announcements"]),
    create=extend_schema(tags=["Announcements"]),
    retrieve=extend_schema(tags=["Announcements"]),
    partial_update=extend_schema(tags=["Announcements"]),
)
class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [CanReadAnnouncements]
    search_fields = ["title", "content", "category__name"]
    ordering_fields = ["is_pinned", "published_at", "created_at"]
    filterset_fields = ["category", "is_pinned", "is_published", "visibility"]

    def get_queryset(self):
        return get_visible_announcements(self.request.user)

    def get_permissions(self):
        if self.action in {"create", "partial_update", "destroy"}:
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        announcement = create_announcement(actor=request.user, validated_data=serializer.validated_data)
        return Response(AnnouncementSerializer(announcement).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        announcement = self.get_object()
        serializer = self.get_serializer(announcement, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        announcement = update_announcement(actor=request.user, announcement=announcement, validated_data=serializer.validated_data)
        return Response(AnnouncementSerializer(announcement).data)

    def destroy(self, request, *args, **kwargs):
        announcement = self.get_object()
        if request.user.role not in {"admin", "moderator"}:
            return Response({"detail": "Only admins or moderators can delete announcements."}, status=status.HTTP_403_FORBIDDEN)
        announcement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
