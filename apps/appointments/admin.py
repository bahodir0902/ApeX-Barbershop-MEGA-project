"""
Appointments app admin configuration.

Provides admin interface for managing appointments and feedbacks.
"""

from django.contrib import admin
from django.db.models import Avg
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Appointment, Feedback


@admin.register(Appointment)
class AppointmentAdmin(ModelAdmin):
    """Admin configuration for Appointment model."""

    list_display = [
        "display_customer",
        "display_barber",
        "barbershop",
        "haircut",
        "appointment_date",
        "appointment_time",
        "display_status",
        "created_at",
    ]
    list_filter = ["status", "is_active", "is_finished", "barbershop", "appointment_date"]
    search_fields = [
        "customer__email",
        "customer__first_name",
        "barber__first_name",
        "barber__last_name",
        "haircut__name",
    ]
    ordering = ["-appointment_date", "-appointment_time"]
    readonly_fields = ["created_at", "updated_at", "idempotency_key"]
    autocomplete_fields = ["barbershop", "barber", "customer", "haircut"]
    date_hierarchy = "appointment_date"

    fieldsets = (
        (None, {"fields": ("barbershop", "barber", "customer", "haircut")}),
        (
            "Schedule",
            {"fields": ("appointment_date", "appointment_time", "duration_minutes")},
        ),
        ("Status", {"fields": ("status", "is_active", "is_finished")}),
        ("Notes", {"fields": ("customer_notes",)}),
        ("Metadata", {"fields": ("idempotency_key", "created_at", "updated_at")}),
    )

    @display(description="Customer")
    def display_customer(self, instance):
        """Display customer name."""
        return instance.customer.full_name

    @display(description="Barber")
    def display_barber(self, instance):
        """Display barber name."""
        return instance.barber.full_name

    @display(
        description="Status",
        label={
            "pending": "warning",
            "confirmed": "info",
            "in_progress": "info",
            "completed": "success",
            "cancelled": "danger",
            "no_show": "danger",
        },
    )
    def display_status(self, instance):
        """Display status with colored badge."""
        return instance.status


@admin.register(Feedback)
class FeedbackAdmin(ModelAdmin):
    """Admin configuration for Feedback model."""

    list_display = [
        "display_customer",
        "display_barber",
        "display_rating",
        "display_has_response",
        "created_at",
    ]
    list_filter = ["rating", "barber", "created_at"]
    search_fields = [
        "customer__email",
        "customer__first_name",
        "barber__first_name",
        "barber__last_name",
        "comment",
    ]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ["appointment", "barber", "customer"]

    fieldsets = (
        (None, {"fields": ("appointment", "barber", "customer")}),
        ("Rating", {"fields": ("rating", "comment")}),
        ("Response", {"fields": ("barber_response", "response_date")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @display(description="Customer")
    def display_customer(self, instance):
        """Display customer name."""
        return instance.customer.full_name

    @display(description="Barber")
    def display_barber(self, instance):
        """Display barber name."""
        return instance.barber.full_name

    @display(description="Rating")
    def display_rating(self, instance):
        """Display rating with stars."""
        return f"{'★' * int(instance.rating)}{'☆' * (5 - int(instance.rating))} ({instance.rating}/5)"

    @display(
        description="Has Response",
        label={"Yes": "success", "No": "warning"},
    )
    def display_has_response(self, instance):
        """Display if feedback has a response."""
        return "Yes" if instance.barber_response else "No"

