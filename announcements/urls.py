"""Announcement URL patterns."""

from django.urls import path

from announcements.views import AnnouncementCategoryViewSet, AnnouncementViewSet


category_list = AnnouncementCategoryViewSet.as_view({"get": "list", "post": "create"})
category_detail = AnnouncementCategoryViewSet.as_view({"get": "retrieve"})
announcement_list = AnnouncementViewSet.as_view({"get": "list", "post": "create"})
announcement_detail = AnnouncementViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})

urlpatterns = [
    path("categories/", category_list, name="announcement-category-list"),
    path("categories/<uuid:pk>/", category_detail, name="announcement-category-detail"),
    path("", announcement_list, name="announcement-list"),
    path("<uuid:pk>/", announcement_detail, name="announcement-detail"),
]
