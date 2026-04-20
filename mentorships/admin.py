from django.contrib import admin

from mentorships.models import MentorProfile, MentorshipFeedback, MentorshipRequest, MentorshipSession


@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "professional_title", "status", "is_accepting_mentees", "approved_by"]
    search_fields = ["user__email", "user__profile__full_name", "professional_title"]
    list_filter = ["status", "is_accepting_mentees"]


@admin.register(MentorshipRequest)
class MentorshipRequestAdmin(admin.ModelAdmin):
    list_display = ["mentor_profile", "mentee", "status", "responded_at", "created_at"]
    search_fields = ["mentor_profile__user__email", "mentee__email", "message"]
    list_filter = ["status", "created_at"]


@admin.register(MentorshipSession)
class MentorshipSessionAdmin(admin.ModelAdmin):
    list_display = ["mentorship_request", "scheduled_at", "status", "created_by"]
    search_fields = ["mentorship_request__mentor_profile__user__email", "meeting_link", "location"]
    list_filter = ["status", "scheduled_at"]


@admin.register(MentorshipFeedback)
class MentorshipFeedbackAdmin(admin.ModelAdmin):
    list_display = ["session", "author", "rating", "created_at"]
    search_fields = ["session__mentorship_request__mentor_profile__user__email", "author__email", "comment"]
    list_filter = ["rating", "created_at"]
