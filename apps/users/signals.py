"""
Users app signals.

Handles signals for user-related events like post-save actions.
"""

from django.contrib.postgres.search import SearchVector
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User


@receiver(post_save, sender=User)
def update_search_vector(sender, instance, **kwargs):
    """
    Update the search vector when a user is saved.
    
    This enables full-text search on user names and email.
    """
    # Avoid recursive saves
    if kwargs.get("raw"):
        return

    User.objects.filter(pk=instance.pk).update(
        search_vector=SearchVector("first_name", "last_name", "email")
    )
