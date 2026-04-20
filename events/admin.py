from django.contrib import admin

from events.models import Event, EventGallery, EventRegistration, EventResult, EventReview, EventSponsor


class EventSponsorInline(admin.TabularInline):
    model = EventSponsor
    extra = 0


class EventGalleryInline(admin.TabularInline):
    model = EventGallery
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["event_name", "event_type", "batch", "year", "status", "is_public", "created_by"]
    search_fields = ["event_name", "slug", "location"]
    list_filter = ["event_type", "status", "is_public", "payment_method", "year"]
    prepopulated_fields = {}
    readonly_fields = ["created_at", "updated_at", "creator_role"]
    inlines = [EventSponsorInline, EventGalleryInline]


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ["event", "user", "status", "payment_status", "ticket_code", "created_at"]
    search_fields = ["event__event_name", "user__email", "ticket_code"]
    list_filter = ["status", "payment_status", "created_at"]
    readonly_fields = ["created_at", "updated_at", "pdf_generated_at", "checked_in_at"]


@admin.register(EventResult)
class EventResultAdmin(admin.ModelAdmin):
    list_display = ["event", "created_by", "created_at"]
    search_fields = ["event__event_name", "result_summary"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(EventReview)
class EventReviewAdmin(admin.ModelAdmin):
    list_display = ["event", "user", "rating", "moderation_status", "created_at"]
    search_fields = ["event__event_name", "user__email", "comment"]
    list_filter = ["rating", "moderation_status", "created_at"]
    readonly_fields = ["created_at", "updated_at"]
