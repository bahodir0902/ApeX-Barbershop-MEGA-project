"""
Appointments app signals.

Handles signals for appointment-related events.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Appointment, Feedback

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Appointment)
def on_appointment_created(sender, instance, created, **kwargs):
    """
    Handle post-save signal for appointments.
    
    Sends confirmation email when appointment is created.
    """
    if created:
        logger.info(
            f"New appointment created: {instance.id} for "
            f"{instance.customer.email} with {instance.barber.full_name}"
        )
        # Trigger async email task
        from apps.appointments.tasks import send_appointment_confirmation_email

        send_appointment_confirmation_email.delay(str(instance.id))


@receiver(post_save, sender=Feedback)
def on_feedback_created(sender, instance, created, **kwargs):
    """
    Handle post-save signal for feedback.
    
    Logs feedback creation for analytics.
    """
    if created:
        logger.info(
            f"New feedback created: {instance.id} - "
            f"Rating: {instance.rating}/5 for barber {instance.barber.full_name}"
        )
