"""Profile API views."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.permissions import IsAdminOrModeratorRole, ReadOnlyOrAuthenticated
from profiles.models import AlumniVerificationRequest
from profiles.permissions import CanManageOwnProfile
from profiles.selectors import get_profile_queryset, get_verification_request_queryset, get_visible_profiles_for_user
from profiles.serializers import (
    AlumniProfileSerializer,
    AlumniProfileUpdateSerializer,
    AlumniVerificationRequestSerializer,
    AlumniVerificationReviewSerializer,
)
from profiles.services import create_verification_request, review_verification_request, update_profile


@extend_schema_view(
    list=extend_schema(tags=["Profiles"]),
    retrieve=extend_schema(tags=["Profiles"]),
    partial_update=extend_schema(tags=["Profiles"]),
)
class AlumniProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AlumniProfileSerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    search_fields = ["full_name", "student_id", "class_roll", "current_city", "current_country"]
    ordering_fields = ["full_name", "batch_year", "created_at"]
    filterset_fields = ["batch_year", "academic_group", "current_city", "current_country"]

    def get_queryset(self):
        return get_visible_profiles_for_user(self.request.user)

    def get_permissions(self):
        if self.action in {"partial_update", "update", "me"}:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in {"partial_update", "update"}:
            return AlumniProfileUpdateSerializer
        return super().get_serializer_class()

    def perform_update(self, serializer):
        update_profile(
            actor=self.request.user,
            profile=self.get_object(),
            validated_data=serializer.validated_data,
        )

    @extend_schema(tags=["Profiles"], responses=AlumniProfileSerializer)
    @action(detail=False, methods=["get", "patch"], permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        profile = get_profile_queryset().get(user=request.user)
        if request.method.lower() == "get":
            return Response(AlumniProfileSerializer(profile, context={"request": request}).data)

        serializer = AlumniProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        update_profile(actor=request.user, profile=profile, validated_data=serializer.validated_data)
        return Response(AlumniProfileSerializer(profile, context={"request": request}).data)


@extend_schema_view(
    list=extend_schema(tags=["Profiles"]),
    create=extend_schema(tags=["Profiles"]),
    retrieve=extend_schema(tags=["Profiles"]),
)
class AlumniVerificationRequestViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniVerificationRequestSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]

    def get_queryset(self):
        return get_verification_request_queryset(self.request.user)

    def create(self, request, *args, **kwargs):
        verification_request = create_verification_request(
            actor=request.user,
            note=request.data.get("note", ""),
        )
        serializer = self.get_serializer(verification_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=["Profiles"],
        request=AlumniVerificationReviewSerializer,
        responses=AlumniVerificationRequestSerializer,
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrModeratorRole])
    def review(self, request, *args, **kwargs):
        verification_request = self.get_object()
        serializer = AlumniVerificationReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review_verification_request(
            actor=request.user,
            verification_request=verification_request,
            **serializer.validated_data,
        )
        return Response(AlumniVerificationRequestSerializer(verification_request).data)
