from django.contrib import admin

from professions.models import Profession


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = [
        "profile",
        "present_occupation",
        "role",
        "institution_or_organization_name",
        "starting_date",
        "ending_date",
        "currently_working_here",
    ]
    search_fields = [
        "profile__full_name",
        "profile__user__email",
        "present_occupation",
        "role",
        "institution_or_organization_name",
    ]
    list_filter = ["currently_working_here", "starting_date"]
    readonly_fields = ["created_at", "updated_at"]
