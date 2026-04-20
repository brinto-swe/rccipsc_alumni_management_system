from django.contrib import admin

from announcements.models import Announcement, AnnouncementCategory


@admin.register(AnnouncementCategory)
class AnnouncementCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "is_pinned", "is_published", "visibility", "published_at"]
    search_fields = ["title", "content", "category__name"]
    list_filter = ["is_pinned", "is_published", "visibility", "category"]
    readonly_fields = ["created_at", "updated_at", "published_at"]
