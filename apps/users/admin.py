"""
Users app admin configuration.

Provides admin interface for managing users with Unfold styling.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Admin configuration for User model."""

    list_display = [
        "email",
        "first_name",
        "last_name",
        "display_role",
        "is_active",
        "is_verified",
        "created_at",
    ]
    list_filter = ["role", "is_active", "is_verified", "is_staff", "created_at"]
    search_fields = ["email", "first_name", "last_name", "phone_number"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at", "last_login"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {"fields": ("first_name", "last_name", "phone_number", "profile_picture")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Settings", {"fields": ("privacy",)}),
        (
            "Important Dates",
            {"fields": ("last_login", "created_at", "updated_at")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "role",
                ),
            },
        ),
    )

    @display(
        description="Role",
        label={
            "client": "info",
            "barber": "warning",
            "owner": "success",
            "admin": "danger",
        },
    )
    def display_role(self, instance):
        """Display user role with colored badge."""
        return instance.role

