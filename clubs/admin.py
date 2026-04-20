from django.contrib import admin

from clubs.models import Club, ClubMembership


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ["name", "visibility", "is_active", "created_by", "created_at"]
    search_fields = ["name", "description"]
    list_filter = ["visibility", "is_active"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ["club", "user", "membership_role", "status", "joined_at"]
    search_fields = ["club__name", "user__email", "user__profile__full_name"]
    list_filter = ["membership_role", "status", "joined_at"]
