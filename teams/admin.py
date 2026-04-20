from django.contrib import admin

from teams.models import Team, TeamEventRegistration, TeamMember


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["name", "sport_type", "batch_year", "captain", "created_by", "is_active"]
    search_fields = ["name", "sport_type", "description"]
    list_filter = ["sport_type", "batch_year", "is_active"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ["team", "user", "role", "is_active", "created_at"]
    search_fields = ["team__name", "user__email", "user__profile__full_name"]
    list_filter = ["role", "is_active"]


@admin.register(TeamEventRegistration)
class TeamEventRegistrationAdmin(admin.ModelAdmin):
    list_display = ["team", "event", "status", "created_by", "created_at"]
    search_fields = ["team__name", "event__event_name"]
    list_filter = ["status", "created_at"]
