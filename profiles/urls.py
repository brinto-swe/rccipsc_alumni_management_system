"""Profile URL patterns."""

from django.urls import path

from profiles.views import AlumniProfileViewSet, AlumniVerificationRequestViewSet


profile_list = AlumniProfileViewSet.as_view({"get": "list"})
profile_detail = AlumniProfileViewSet.as_view({"get": "retrieve", "patch": "partial_update"})
profile_me = AlumniProfileViewSet.as_view({"get": "me", "patch": "me"})

verification_list = AlumniVerificationRequestViewSet.as_view({"get": "list", "post": "create"})
verification_detail = AlumniVerificationRequestViewSet.as_view({"get": "retrieve"})
verification_review = AlumniVerificationRequestViewSet.as_view({"post": "review"})

urlpatterns = [
    path("", profile_list, name="profile-list"),
    path("me/", profile_me, name="profile-me"),
    path("<uuid:pk>/", profile_detail, name="profile-detail"),
    path("verification-requests/", verification_list, name="verification-request-list"),
    path("verification-requests/<uuid:pk>/", verification_detail, name="verification-request-detail"),
    path(
        "verification-requests/<uuid:pk>/review/",
        verification_review,
        name="verification-request-review",
    ),
]
