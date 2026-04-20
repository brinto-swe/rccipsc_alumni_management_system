from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["email"]
    list_display = [
        "email",
        "role",
        "account_status",
        "managed_batch_year",
        "is_active",
        "is_verified",
        "is_staff",
        "date_joined",
    ]
    search_fields = ["email", "username", "profile__full_name"]
    list_filter = ["role", "account_status", "is_active", "is_verified", "is_staff"]
    readonly_fields = ["date_joined", "last_login", "created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Identity",
            {
                "fields": (
                    "username",
                    "role",
                    "managed_batch_year",
                    "account_status",
                    "is_verified",
                    "email_verified_at",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role", "account_status"),
            },
        ),
    )
