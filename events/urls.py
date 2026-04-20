"""Event URL patterns."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from events.views import (
    EventGalleryViewSet,
    EventRegistrationViewSet,
    EventResultViewSet,
    EventReviewViewSet,
    EventSponsorViewSet,
    EventViewSet,
)


event_list = EventViewSet.as_view({"get": "list", "post": "create"})
event_detail = EventViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})
event_previous = EventViewSet.as_view({"get": "previous"})
event_register = EventViewSet.as_view({"post": "register"})
event_participants = EventViewSet.as_view({"get": "participants"})

resource_router = DefaultRouter()
resource_router.register("registrations", EventRegistrationViewSet, basename="event-registration")
resource_router.register("sponsors", EventSponsorViewSet, basename="event-sponsor")
resource_router.register("gallery", EventGalleryViewSet, basename="event-gallery")
resource_router.register("results", EventResultViewSet, basename="event-result")
resource_router.register("reviews", EventReviewViewSet, basename="event-review")

urlpatterns = [
    path("", event_list, name="event-list"),
    path("previous/", event_previous, name="event-previous"),
    path("<uuid:pk>/", event_detail, name="event-detail"),
    path("<uuid:pk>/register/", event_register, name="event-register"),
    path("<uuid:pk>/participants/", event_participants, name="event-participants"),
    path("", include(resource_router.urls)),
]
