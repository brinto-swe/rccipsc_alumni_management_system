"""Event API views."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.permissions import IsAdminRole
from events.models import Event, EventGallery, EventRegistration, EventResult, EventReview, EventSponsor
from events.permissions import CanReadVisibleEvents, IsEventManager
from events.selectors import (
    get_gallery_queryset,
    get_previous_event_queryset,
    get_registration_queryset,
    get_visible_event_queryset,
)
from events.serializers import (
    EventDetailSerializer,
    EventGallerySerializer,
    EventListSerializer,
    EventRegistrationCreateSerializer,
    EventRegistrationSerializer,
    EventResultSerializer,
    EventReviewSerializer,
    EventSponsorSerializer,
    EventWriteSerializer,
)
from events.services import (
    add_gallery_item,
    create_event,
    create_event_review,
    delete_event,
    register_for_event,
    update_event,
    upsert_event_result,
)


@extend_schema_view(
    list=extend_schema(tags=["Events"]),
    retrieve=extend_schema(tags=["Events"]),
    create=extend_schema(tags=["Events"]),
    partial_update=extend_schema(tags=["Events"]),
    destroy=extend_schema(tags=["Events"]),
)
class EventViewSet(viewsets.ModelViewSet):
    permission_classes = [CanReadVisibleEvents]
    search_fields = ["event_name", "location", "invitation_letter"]
    ordering_fields = ["event_start_date", "event_date", "registration_end_date", "created_at"]
    filterset_fields = ["event_type", "status", "is_public", "batch", "year", "payment_method"]

    def get_queryset(self):
        return get_visible_event_queryset(self.request.user)

    def get_serializer_class(self):
        if self.action in {"list", "previous"}:
            return EventListSerializer
        if self.action in {"create", "update", "partial_update"}:
            return EventWriteSerializer
        return EventDetailSerializer

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "register"}:
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = create_event(actor=request.user, validated_data=serializer.validated_data)
        return Response(EventDetailSerializer(event, context={"request": request}).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        event = self.get_object()
        serializer = self.get_serializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        event = update_event(actor=request.user, event=event, validated_data=serializer.validated_data)
        return Response(EventDetailSerializer(event, context={"request": request}).data)

    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        delete_event(actor=request.user, event=event)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(tags=["Events"], request=EventRegistrationCreateSerializer, responses=EventRegistrationSerializer)
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def register(self, request, *args, **kwargs):
        event = self.get_object()
        serializer = EventRegistrationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registration = register_for_event(event=event, actor=request.user, **serializer.validated_data)
        return Response(EventRegistrationSerializer(registration, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=["Events"], responses=EventListSerializer(many=True))
    @action(detail=False, methods=["get"])
    def previous(self, request, *args, **kwargs):
        queryset = get_previous_event_queryset(request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EventListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        serializer = EventListSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    @extend_schema(tags=["Events"], responses=EventRegistrationSerializer(many=True))
    @action(detail=True, methods=["get"])
    def participants(self, request, *args, **kwargs):
        event = self.get_object()
        queryset = event.registrations.select_related("user").filter(attendee_visibility="public")
        serializer = EventRegistrationSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=["Events"]),
    retrieve=extend_schema(tags=["Events"]),
)
class EventRegistrationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "payment_status", "event"]
    ordering_fields = ["created_at", "status"]

    def get_queryset(self):
        return get_registration_queryset(self.request.user)


@extend_schema_view(
    list=extend_schema(tags=["Events"]),
    create=extend_schema(tags=["Events"]),
    destroy=extend_schema(tags=["Events"]),
)
class EventGalleryViewSet(viewsets.ModelViewSet):
    serializer_class = EventGallerySerializer
    permission_classes = [CanReadVisibleEvents]
    http_method_names = ["get", "post", "delete"]
    filterset_fields = ["event", "is_public"]

    def get_queryset(self):
        return get_gallery_queryset(self.request.user)

    def get_permissions(self):
        if self.action in {"create", "destroy"}:
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        gallery_item = add_gallery_item(
            actor=request.user,
            event=serializer.validated_data["event"],
            validated_data={key: value for key, value in serializer.validated_data.items() if key != "event"},
        )
        return Response(EventGallerySerializer(gallery_item, context={"request": request}).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        gallery_item = self.get_object()
        if request.user.role != "admin" and gallery_item.event.created_by_id != request.user.id:
            return Response({"detail": "You cannot remove this gallery item."}, status=status.HTTP_403_FORBIDDEN)
        gallery_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(tags=["Events"]),
    create=extend_schema(tags=["Events"]),
    partial_update=extend_schema(tags=["Events"]),
)
class EventResultViewSet(viewsets.ModelViewSet):
    serializer_class = EventResultSerializer
    permission_classes = [CanReadVisibleEvents]
    http_method_names = ["get", "post", "patch"]

    def get_queryset(self):
        return EventResult.objects.select_related("event", "created_by")

    def get_permissions(self):
        if self.action in {"create", "partial_update"}:
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.validated_data["event"]
        result = upsert_event_result(
            actor=request.user,
            event=event,
            validated_data={key: value for key, value in serializer.validated_data.items() if key != "event"},
        )
        return Response(EventResultSerializer(result).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        result = self.get_object()
        serializer = self.get_serializer(result, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        result = upsert_event_result(
            actor=request.user,
            event=result.event,
            validated_data={key: value for key, value in serializer.validated_data.items() if key != "event"},
        )
        return Response(EventResultSerializer(result).data)


@extend_schema_view(
    list=extend_schema(tags=["Events"]),
    create=extend_schema(tags=["Events"]),
    partial_update=extend_schema(tags=["Events"]),
    destroy=extend_schema(tags=["Events"]),
)
class EventReviewViewSet(viewsets.ModelViewSet):
    serializer_class = EventReviewSerializer
    permission_classes = [CanReadVisibleEvents]
    http_method_names = ["get", "post", "patch", "delete"]
    filterset_fields = ["event", "rating", "moderation_status"]

    def get_queryset(self):
        queryset = EventReview.objects.select_related("event", "user").order_by("-created_at")
        if self.request.user.is_authenticated and self.request.user.role == "admin":
            return queryset
        return queryset.filter(moderation_status="approved")

    def get_permissions(self):
        if self.action in {"create", "partial_update", "destroy"}:
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.validated_data["event"]
        review = create_event_review(
            actor=request.user,
            event=event,
            validated_data={key: value for key, value in serializer.validated_data.items() if key != "event"},
        )
        return Response(EventReviewSerializer(review, context={"request": request}).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        review = self.get_object()
        if request.user.role != "admin" and review.user_id != request.user.id:
            return Response({"detail": "You may only edit your own review."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        review = create_event_review(
            actor=request.user,
            event=review.event,
            validated_data={key: value for key, value in serializer.validated_data.items() if key != "event"},
        )
        return Response(EventReviewSerializer(review, context={"request": request}).data)

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        if request.user.role != "admin" and review.user_id != request.user.id:
            return Response({"detail": "You may only delete your own review."}, status=status.HTTP_403_FORBIDDEN)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(tags=["Events"]),
    create=extend_schema(tags=["Events"]),
    destroy=extend_schema(tags=["Events"]),
)
class EventSponsorViewSet(viewsets.ModelViewSet):
    serializer_class = EventSponsorSerializer
    queryset = EventSponsor.objects.select_related("event", "created_by").order_by("sponsor_name")
    permission_classes = [CanReadVisibleEvents]
    http_method_names = ["get", "post", "delete"]

    def get_permissions(self):
        if self.action in {"create", "destroy"}:
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.validated_data["event"]
        if request.user.role != "admin" and event.created_by_id != request.user.id:
            return Response({"detail": "You cannot manage sponsors for this event."}, status=status.HTTP_403_FORBIDDEN)
        sponsor = serializer.save(created_by=request.user, updated_by=request.user)
        return Response(EventSponsorSerializer(sponsor, context={"request": request}).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        sponsor = self.get_object()
        if request.user.role != "admin" and sponsor.event.created_by_id != request.user.id:
            return Response({"detail": "You cannot manage sponsors for this event."}, status=status.HTTP_403_FORBIDDEN)
        sponsor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Events"])
class AdminEventViewSet(EventViewSet):
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return Event.objects.select_related("created_by", "updated_by").prefetch_related("sponsors")

    def get_permissions(self):
        return [IsAdminRole()]
