"""Views for notifications and broadcasts."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.models import NotificationPreference
from notifications.permissions import CanAccessOwnNotifications, IsAdminOrModeratorNotifier
from notifications.selectors import get_email_queue_queryset, get_notification_queryset
from notifications.serializers import (
    AdminBroadcastSerializer,
    EmailQueueSerializer,
    NotificationPreferenceSerializer,
    NotificationSerializer,
)
from notifications.services import create_admin_broadcast, mark_notification_as_read


@extend_schema_view(
    list=extend_schema(tags=["Notifications"]),
    retrieve=extend_schema(tags=["Notifications"]),
)
class NotificationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [CanAccessOwnNotifications]
    filterset_fields = ["is_read", "notification_type"]
    ordering_fields = ["created_at", "read_at"]

    def get_queryset(self):
        return get_notification_queryset(self.request.user)

    @extend_schema(tags=["Notifications"], request=None, responses=NotificationSerializer)
    @action(detail=True, methods=["post"])
    def mark_read(self, request, *args, **kwargs):
        notification = self.get_object()
        notification = mark_notification_as_read(actor=request.user, notification=notification)
        return Response(NotificationSerializer(notification).data)


@extend_schema(tags=["Notifications"])
class NotificationPreferenceViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = NotificationPreference.objects.order_by("created_at")
        if self.request.user.role == "admin":
            return queryset
        return queryset.filter(user=self.request.user)


@extend_schema(tags=["Notifications"], request=AdminBroadcastSerializer)
class AdminBroadcastAPIView(GenericAPIView):
    serializer_class = AdminBroadcastSerializer
    permission_classes = [IsAdminOrModeratorNotifier]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create_admin_broadcast(actor=request.user, **serializer.validated_data)
        return Response({"detail": "Broadcast queued successfully."}, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Notifications"])
class EmailQueueViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = EmailQueueSerializer
    permission_classes = [IsAdminOrModeratorNotifier]
    filterset_fields = ["status"]

    def get_queryset(self):
        return get_email_queue_queryset(self.request.user)
