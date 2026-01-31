"""
Barbershops app signals.

Handles signals for search vector updates.
"""

from django.contrib.postgres.search import SearchVector
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Barber, Barbershop, Haircut


@receiver(post_save, sender=Barbershop)
def update_barbershop_search_vector(sender, instance, **kwargs):
    """
    Update the search vector when a barbershop is saved.
    """
    if kwargs.get("raw"):
        return

    Barbershop.objects.filter(pk=instance.pk).update(
        search_vector=SearchVector("name", "address", "description")
    )


@receiver(post_save, sender=Barber)
def update_barber_search_vector(sender, instance, **kwargs):
    """
    Update the search vector when a barber is saved.
    """
    if kwargs.get("raw"):
        return

    Barber.objects.filter(pk=instance.pk).update(
        search_vector=SearchVector("first_name", "last_name", "bio")
    )


@receiver(post_save, sender=Haircut)
def update_haircut_search_vector(sender, instance, **kwargs):
    """
    Update the search vector when a haircut is saved.
    """
    if kwargs.get("raw"):
        return

    Haircut.objects.filter(pk=instance.pk).update(
        search_vector=SearchVector("name", "description")
    )
