"""
Barbershops app configuration.
"""

from django.apps import AppConfig


class BarbershopsConfig(AppConfig):
    """Configuration for the barbershops app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.barbershops"
    verbose_name = "Barbershops"

    def ready(self):
        """Import signals when app is ready."""
        import apps.barbershops.signals  # noqa: F401

