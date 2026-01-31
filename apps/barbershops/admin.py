"""
Barbershops app admin configuration.

Provides admin interface for managing barbershops, barbers, and haircuts.
"""

from django.contrib import admin
from django.db.models import Avg, Count
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import Barber, BarberHaircut, Barbershop, Haircut


class BarberInline(TabularInline):
    """Inline admin for barbers within a barbershop."""

    model = Barber
    extra = 0
    fields = ["first_name", "last_name", "phone_number", "is_active"]
    readonly_fields = []


class HaircutInline(TabularInline):
    """Inline admin for haircuts within a barbershop."""

    model = Haircut
    extra = 0
    fields = ["name", "price", "duration_minutes", "is_active"]
    readonly_fields = []


class BarberHaircutInline(TabularInline):
    """Inline admin for barber-haircut associations."""

    model = BarberHaircut
    extra = 0
    fields = ["haircut"]
    autocomplete_fields = ["haircut"]


@admin.register(Barbershop)
class BarbershopAdmin(ModelAdmin):
    """Admin configuration for Barbershop model."""

    list_display = [
        "name",
        "address",
        "owner",
        "display_barber_count",
        "display_status",
        "created_at",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "address", "owner__email"]
    ordering = ["name"]
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ["owner"]
    inlines = [BarberInline, HaircutInline]

    fieldsets = (
        (None, {"fields": ("name", "owner")}),
        ("Location", {"fields": ("address", "latitude", "longitude")}),
        ("Contact", {"fields": ("phone_number",)}),
        ("Media", {"fields": ("picture", "description")}),
        ("Status", {"fields": ("is_active",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        """Annotate queryset with barber count."""
        return super().get_queryset(request).annotate(
            barber_count=Count("barbers")
        )

    @display(description="Barbers")
    def display_barber_count(self, instance):
        """Display barber count."""
        return getattr(instance, "barber_count", 0)

    @display(
        description="Status",
        label={"Active": "success", "Inactive": "danger"},
    )
    def display_status(self, instance):
        """Display status with colored badge."""
        return "Active" if instance.is_active else "Inactive"


@admin.register(Barber)
class BarberAdmin(ModelAdmin):
    """Admin configuration for Barber model."""

    list_display = [
        "full_name",
        "barbershop",
        "phone_number",
        "display_experience",
        "display_rating",
        "display_status",
        "created_at",
    ]
    list_filter = ["is_active", "barbershop", "created_at"]
    search_fields = ["first_name", "last_name", "email", "phone_number"]
    ordering = ["first_name", "last_name"]
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ["barbershop", "user"]
    inlines = [BarberHaircutInline]

    fieldsets = (
        (None, {"fields": ("user", "barbershop")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email", "phone_number")}),
        ("Professional", {"fields": ("picture", "bio", "experienced_years")}),
        (
            "Schedule",
            {
                "fields": (
                    "working_start_time",
                    "working_end_time",
                    "break_start_time",
                    "break_end_time",
                    "working_days",
                )
            },
        ),
        ("Status", {"fields": ("is_active",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        """Annotate queryset with average rating."""
        return super().get_queryset(request).annotate(
            avg_rating=Avg("feedbacks__rating")
        )

    @display(description="Name")
    def full_name(self, instance):
        """Display full name."""
        return instance.full_name

    @display(description="Experience")
    def display_experience(self, instance):
        """Display experience years."""
        return f"{instance.experienced_years} years"

    @display(description="Rating")
    def display_rating(self, instance):
        """Display average rating."""
        rating = getattr(instance, "avg_rating", None)
        if rating:
            return f"{rating:.1f}/5.0"
        return "N/A"

    @display(
        description="Status",
        label={"Active": "success", "Inactive": "danger"},
    )
    def display_status(self, instance):
        """Display status with colored badge."""
        return "Active" if instance.is_active else "Inactive"


@admin.register(Haircut)
class HaircutAdmin(ModelAdmin):
    """Admin configuration for Haircut model."""

    list_display = [
        "name",
        "barbershop",
        "display_price",
        "display_duration",
        "display_status",
        "created_at",
    ]
    list_filter = ["is_active", "barbershop", "created_at"]
    search_fields = ["name", "description", "barbershop__name"]
    ordering = ["name", "price"]
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ["barbershop"]

    fieldsets = (
        (None, {"fields": ("name", "barbershop")}),
        ("Details", {"fields": ("description", "price", "duration_minutes")}),
        ("Media", {"fields": ("picture",)}),
        ("Status", {"fields": ("is_active",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @display(description="Price")
    def display_price(self, instance):
        """Display formatted price."""
        return f"${instance.price:,.2f}"

    @display(description="Duration")
    def display_duration(self, instance):
        """Display duration in minutes."""
        return f"{instance.duration_minutes} min"

    @display(
        description="Status",
        label={"Active": "success", "Inactive": "danger"},
    )
    def display_status(self, instance):
        """Display status with colored badge."""
        return "Active" if instance.is_active else "Inactive"

