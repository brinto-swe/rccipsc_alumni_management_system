from django.contrib import admin

from accounts.models import AccountAuditLog


@admin.register(AccountAuditLog)
class AccountAuditLogAdmin(admin.ModelAdmin):
    list_display = ["action", "actor", "target_user", "ip_address", "created_at"]
    search_fields = ["action", "actor__email", "target_user__email", "message"]
    list_filter = ["action", "created_at"]
    readonly_fields = ["created_at", "updated_at"]
