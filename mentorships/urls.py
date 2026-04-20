"""Mentorship URL patterns."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from mentorships.views import MentorProfileViewSet, MentorshipFeedbackViewSet, MentorshipRequestViewSet, MentorshipSessionViewSet


router = DefaultRouter()
router.register("mentors", MentorProfileViewSet, basename="mentor-profile")
router.register("requests", MentorshipRequestViewSet, basename="mentorship-request")
router.register("sessions", MentorshipSessionViewSet, basename="mentorship-session")
router.register("feedback", MentorshipFeedbackViewSet, basename="mentorship-feedback")

urlpatterns = [
    path("", include(router.urls)),
]
