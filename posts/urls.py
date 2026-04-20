"""Public and member feed URL patterns."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from posts.views import CommentViewSet, PostViewSet, ReactionViewSet, ReportViewSet


post_list = PostViewSet.as_view({"get": "list", "post": "create"})
post_detail = PostViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})

router = DefaultRouter()
router.register("comments", CommentViewSet, basename="post-comment")
router.register("reactions", ReactionViewSet, basename="post-reaction")
router.register("reports", ReportViewSet, basename="post-report")

urlpatterns = [
    path("", post_list, name="post-list"),
    path("<uuid:pk>/", post_detail, name="post-detail"),
    path("", include(router.urls)),
]
