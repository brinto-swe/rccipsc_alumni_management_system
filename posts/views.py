"""Views for the alumni social feed."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from posts.models import Report
from posts.permissions import CanReadPosts, IsModeratorOrAdminContentManager
from posts.selectors import get_comment_queryset, get_reaction_queryset, get_report_queryset, get_visible_post_queryset
from posts.serializers import (
    CommentSerializer,
    PostSerializer,
    PostWriteSerializer,
    ReactionSerializer,
    ReportReviewSerializer,
    ReportSerializer,
)
from posts.services import (
    create_comment,
    create_post,
    create_report,
    review_report,
    set_reaction,
    soft_delete_comment,
    soft_delete_post,
    update_comment,
    update_post,
)


@extend_schema_view(
    list=extend_schema(tags=["Posts"]),
    retrieve=extend_schema(tags=["Posts"]),
    create=extend_schema(tags=["Posts"]),
    partial_update=extend_schema(tags=["Posts"]),
    destroy=extend_schema(tags=["Posts"]),
)
class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [CanReadPosts]
    search_fields = ["content", "author__email", "author__profile__full_name"]
    ordering_fields = ["published_at", "created_at"]
    filterset_fields = ["visibility", "is_published"]

    def get_queryset(self):
        return get_visible_post_queryset(self.request.user)

    def get_serializer_class(self):
        if self.action in {"create", "partial_update", "update"}:
            return PostWriteSerializer
        return PostSerializer

    def get_permissions(self):
        if self.action in {"create", "partial_update", "destroy"}:
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = create_post(actor=request.user, validated_data=serializer.validated_data)
        return Response(PostSerializer(post, context={"request": request}).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        post = update_post(actor=request.user, post=post, validated_data=serializer.validated_data)
        return Response(PostSerializer(post, context={"request": request}).data)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        soft_delete_post(actor=request.user, post=post)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(tags=["Posts"]),
    create=extend_schema(tags=["Posts"]),
    partial_update=extend_schema(tags=["Posts"]),
    destroy=extend_schema(tags=["Posts"]),
)
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [CanReadPosts]
    http_method_names = ["get", "post", "patch", "delete"]
    filterset_fields = ["post", "parent"]

    def get_queryset(self):
        return get_comment_queryset(self.request.user)

    def get_permissions(self):
        if self.action in {"create", "partial_update", "destroy"}:
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = create_comment(actor=request.user, validated_data=serializer.validated_data)
        return Response(CommentSerializer(comment, context={"request": request}).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        comment = self.get_object()
        serializer = self.get_serializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        comment = update_comment(actor=request.user, comment=comment, validated_data=serializer.validated_data)
        return Response(CommentSerializer(comment, context={"request": request}).data)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        soft_delete_comment(actor=request.user, comment=comment)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(tags=["Posts"]),
    create=extend_schema(tags=["Posts"]),
    destroy=extend_schema(tags=["Posts"]),
)
class ReactionViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = ReactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["post", "reaction_type"]

    def get_queryset(self):
        return get_reaction_queryset(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reaction = set_reaction(actor=request.user, validated_data=serializer.validated_data)
        return Response(ReactionSerializer(reaction, context={"request": request}).data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(tags=["Posts"]),
    create=extend_schema(tags=["Posts"]),
    partial_update=extend_schema(tags=["Posts"]),
)
class ReportViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_report_queryset(self.request.user)

    def get_serializer_class(self):
        if self.action in {"partial_update", "update"}:
            return ReportReviewSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = ReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = create_report(actor=request.user, validated_data=serializer.validated_data)
        return Response(ReportSerializer(report, context={"request": request}).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        report = self.get_object()
        serializer = ReportReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = review_report(actor=request.user, report=report, **serializer.validated_data)
        return Response(ReportSerializer(report, context={"request": request}).data)


class AdminReportViewSet(ReportViewSet):
    permission_classes = [IsModeratorOrAdminContentManager]

    def get_permissions(self):
        return [IsModeratorOrAdminContentManager()]
