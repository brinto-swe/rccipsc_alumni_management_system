"""Team URL patterns."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from teams.views import TeamEventRegistrationViewSet, TeamMemberViewSet, TeamViewSet


team_list = TeamViewSet.as_view({"get": "list", "post": "create"})
team_detail = TeamViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})

router = DefaultRouter()
router.register("members", TeamMemberViewSet, basename="team-member")
router.register("registrations", TeamEventRegistrationViewSet, basename="team-event-registration")

urlpatterns = [
    path("", team_list, name="team-list"),
    path("<uuid:pk>/", team_detail, name="team-detail"),
    path("", include(router.urls)),
]
