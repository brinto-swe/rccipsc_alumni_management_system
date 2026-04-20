from django.contrib import admin

from profiles.models import AlumniProfile, AlumniVerificationRequest


@admin.register(AlumniProfile)
class AlumniProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "user", "batch_year", "academic_group", "current_city", "directory_visibility"]
    search_fields = ["full_name", "user__email", "student_id", "class_roll"]
    list_filter = ["academic_group", "batch_year", "directory_visibility", "email_visibility"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(AlumniVerificationRequest)
class AlumniVerificationRequestAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "reviewed_by", "reviewed_at", "created_at"]
    search_fields = ["user__email", "note", "review_note"]
    list_filter = ["status", "created_at"]
    readonly_fields = ["created_at", "updated_at"]
