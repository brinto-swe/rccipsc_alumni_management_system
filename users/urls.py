"""URL patterns for user APIs."""

from django.urls import path

from users.views import CurrentUserAPIView


urlpatterns = [
    path("me/", CurrentUserAPIView.as_view(), name="user-me"),
]
