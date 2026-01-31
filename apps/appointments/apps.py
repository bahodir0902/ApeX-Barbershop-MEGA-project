"""
Appointments app configuration.
"""

from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    """Configuration for the appointments app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.appointments"
    verbose_name = "Appointments"

    def ready(self):
        """Import signals when app is ready."""
        import apps.appointments.signals  # noqa: F401

