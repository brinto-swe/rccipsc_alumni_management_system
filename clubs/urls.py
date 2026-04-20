"""Club URL patterns."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from clubs.views import ClubMembershipViewSet, ClubViewSet


club_list = ClubViewSet.as_view({"get": "list", "post": "create"})
club_detail = ClubViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})
club_join = ClubViewSet.as_view({"post": "join"})

router = DefaultRouter()
router.register("memberships", ClubMembershipViewSet, basename="club-membership")

urlpatterns = [
    path("", club_list, name="club-list"),
    path("<uuid:pk>/", club_detail, name="club-detail"),
    path("<uuid:pk>/join/", club_join, name="club-join"),
    path("", include(router.urls)),
]
