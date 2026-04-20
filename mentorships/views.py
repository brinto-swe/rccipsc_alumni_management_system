"""Views for mentorship APIs."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mentorships.selectors import (
    get_mentor_queryset,
    get_mentorship_feedback_queryset,
    get_mentorship_request_queryset,
    get_mentorship_session_queryset,
)
from mentorships.serializers import (
    MentorProfileReviewSerializer,
    MentorProfileSerializer,
    MentorshipFeedbackSerializer,
    MentorshipRequestResponseSerializer,
    MentorshipRequestSerializer,
    MentorshipSessionSerializer,
)
from mentorships.services import (
    apply_as_mentor,
    create_mentorship_request,
    respond_to_request,
    review_mentor_profile,
    schedule_session,
    submit_feedback,
)


@extend_schema_view(
    list=extend_schema(tags=["Mentorship"]),
    create=extend_schema(tags=["Mentorship"]),
    retrieve=extend_schema(tags=["Mentorship"]),
    partial_update=extend_schema(tags=["Mentorship"]),
)
class MentorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = MentorProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch"]
    search_fields = ["professional_title", "bio", "user__profile__full_name"]
    filterset_fields = ["status", "is_accepting_mentees"]

    def get_queryset(self):
        return get_mentor_queryset(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mentor_profile = apply_as_mentor(actor=request.user, validated_data=serializer.validated_data)
        return Response(MentorProfileSerializer(mentor_profile).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        mentor_profile = self.get_object()
        if request.user.id != mentor_profile.user_id and request.user.role != "admin":
            return Response({"detail": "You can only update your own mentor profile."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(mentor_profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(mentor_profile, field, value)
        mentor_profile.updated_by = request.user
        mentor_profile.save()
        return Response(MentorProfileSerializer(mentor_profile).data)

    @extend_schema(tags=["Mentorship"], request=MentorProfileReviewSerializer, responses=MentorProfileSerializer)
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def review(self, request, *args, **kwargs):
        mentor_profile = self.get_object()
        serializer = MentorProfileReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mentor_profile = review_mentor_profile(actor=request.user, mentor_profile=mentor_profile, **serializer.validated_data)
        return Response(MentorProfileSerializer(mentor_profile).data)


@extend_schema_view(
    list=extend_schema(tags=["Mentorship"]),
    create=extend_schema(tags=["Mentorship"]),
)
class MentorshipRequestViewSet(viewsets.ModelViewSet):
    serializer_class = MentorshipRequestSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]
    filterset_fields = ["mentor_profile", "status"]

    def get_queryset(self):
        return get_mentorship_request_queryset(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mentorship_request = create_mentorship_request(actor=request.user, validated_data=serializer.validated_data)
        return Response(MentorshipRequestSerializer(mentorship_request).data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=["Mentorship"], request=MentorshipRequestResponseSerializer, responses=MentorshipRequestSerializer)
    @action(detail=True, methods=["post"])
    def accept(self, request, *args, **kwargs):
        mentorship_request = self.get_object()
        serializer = MentorshipRequestResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mentorship_request = respond_to_request(
            actor=request.user,
            mentorship_request=mentorship_request,
            status="accepted",
            **serializer.validated_data,
        )
        return Response(MentorshipRequestSerializer(mentorship_request).data)

    @extend_schema(tags=["Mentorship"], request=MentorshipRequestResponseSerializer, responses=MentorshipRequestSerializer)
    @action(detail=True, methods=["post"])
    def reject(self, request, *args, **kwargs):
        mentorship_request = self.get_object()
        serializer = MentorshipRequestResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mentorship_request = respond_to_request(
            actor=request.user,
            mentorship_request=mentorship_request,
            status="rejected",
            **serializer.validated_data,
        )
        return Response(MentorshipRequestSerializer(mentorship_request).data)


@extend_schema_view(
    list=extend_schema(tags=["Mentorship"]),
    create=extend_schema(tags=["Mentorship"]),
    partial_update=extend_schema(tags=["Mentorship"]),
)
class MentorshipSessionViewSet(viewsets.ModelViewSet):
    serializer_class = MentorshipSessionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch"]
    filterset_fields = ["mentorship_request", "status"]

    def get_queryset(self):
        return get_mentorship_session_queryset(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = schedule_session(actor=request.user, validated_data=serializer.validated_data)
        return Response(MentorshipSessionSerializer(session).data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(tags=["Mentorship"]),
    create=extend_schema(tags=["Mentorship"]),
)
class MentorshipFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = MentorshipFeedbackSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]
    filterset_fields = ["session", "rating"]

    def get_queryset(self):
        return get_mentorship_feedback_queryset(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feedback = submit_feedback(actor=request.user, validated_data=serializer.validated_data)
        return Response(MentorshipFeedbackSerializer(feedback).data, status=status.HTTP_201_CREATED)
