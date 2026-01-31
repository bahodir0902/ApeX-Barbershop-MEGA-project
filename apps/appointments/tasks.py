"""
Celery tasks for Appointments app.

Provides asynchronous tasks for appointment-related operations.
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_appointment_confirmation_email(self, appointment_id):
    """
    Send appointment confirmation email to customer.
    
    Args:
        appointment_id: The ID of the appointment.
    """
    try:
        from apps.appointments.models import Appointment

        appointment = Appointment.objects.select_related(
            "customer", "barber", "barbershop", "haircut"
        ).get(id=appointment_id)

        subject = "Appointment Confirmation - ApeX Barbershop"
        html_message = render_to_string(
            "emails/appointment_confirmation.html",
            {
                "appointment": appointment,
                "customer": appointment.customer,
                "barber": appointment.barber,
                "barbershop": appointment.barbershop,
                "haircut": appointment.haircut,
                "year": timezone.now().year,
            },
        )
        plain_message = (
            f"Your appointment has been confirmed!\n\n"
            f"Date: {appointment.appointment_date}\n"
            f"Time: {appointment.appointment_time}\n"
            f"Barber: {appointment.barber.full_name}\n"
            f"Location: {appointment.barbershop.name}\n"
        )

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.customer.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Confirmation email sent for appointment {appointment_id}")

    except Exception as e:
        logger.error(f"Failed to send confirmation email: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_appointment_reminder_email(self, appointment_id):
    """
    Send appointment reminder email to customer.
    
    Args:
        appointment_id: The ID of the appointment.
    """
    try:
        from apps.appointments.models import Appointment

        appointment = Appointment.objects.select_related(
            "customer", "barber", "barbershop", "haircut"
        ).get(id=appointment_id)

        subject = "Appointment Reminder - ApeX Barbershop"
        html_message = render_to_string(
            "emails/appointment_reminder.html",
            {
                "appointment": appointment,
                "customer": appointment.customer,
                "barber": appointment.barber,
                "barbershop": appointment.barbershop,
                "haircut": appointment.haircut,
                "year": timezone.now().year,
            },
        )
        plain_message = (
            f"Reminder: You have an upcoming appointment!\n\n"
            f"Date: {appointment.appointment_date}\n"
            f"Time: {appointment.appointment_time}\n"
            f"Barber: {appointment.barber.full_name}\n"
            f"Location: {appointment.barbershop.name}\n"
        )

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.customer.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Reminder email sent for appointment {appointment_id}")

    except Exception as e:
        logger.error(f"Failed to send reminder email: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task
def send_appointment_reminders():
    """
    Send reminder emails for appointments happening tomorrow.
    
    This task runs hourly and sends reminders for appointments
    scheduled for the next day.
    """
    from apps.appointments.models import Appointment

    tomorrow = timezone.now().date() + timedelta(days=1)
    
    # Get active appointments for tomorrow that haven't been reminded
    appointments = Appointment.objects.filter(
        appointment_date=tomorrow,
        is_active=True,
        is_finished=False,
        status__in=["pending", "confirmed"],
    ).select_related("customer")

    reminder_count = 0
    for appointment in appointments:
        try:
            send_appointment_reminder_email.delay(str(appointment.id))
            reminder_count += 1
        except Exception as e:
            logger.error(f"Failed to queue reminder for {appointment.id}: {e}")

    logger.info(f"Queued {reminder_count} appointment reminders for {tomorrow}")


@shared_task
def generate_daily_reports():
    """
    Generate daily reports for barbershop owners.
    
    This task runs at the end of each day and sends a summary
    of the day's appointments and revenue.
    """
    from apps.appointments.models import Appointment
    from apps.barbershops.models import Barbershop

    today = timezone.now().date()

    for barbershop in Barbershop.objects.filter(is_active=True).select_related("owner"):
        try:
            # Get today's appointments
            appointments = Appointment.objects.filter(
                barbershop=barbershop,
                appointment_date=today,
            )

            total_appointments = appointments.count()
            completed_appointments = appointments.filter(is_finished=True).count()
            cancelled_appointments = appointments.filter(is_active=False).count()
            
            # Calculate revenue
            revenue = (
                appointments.filter(is_finished=True)
                .aggregate(total=Sum("haircut__price"))["total"]
                or 0
            )

            if total_appointments > 0:
                subject = f"Daily Report - {barbershop.name} - {today}"
                html_message = render_to_string(
                    "emails/daily_report.html",
                    {
                        "barbershop": barbershop,
                        "date": today,
                        "total_appointments": total_appointments,
                        "completed_appointments": completed_appointments,
                        "cancelled_appointments": cancelled_appointments,
                        "revenue": revenue,
                        "year": timezone.now().year,
                    },
                )

                send_mail(
                    subject=subject,
                    message=f"Daily report for {barbershop.name}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[barbershop.owner.email],
                    html_message=html_message,
                    fail_silently=False,
                )

                logger.info(f"Daily report sent for {barbershop.name}")

        except Exception as e:
            logger.error(f"Failed to send daily report for {barbershop.name}: {e}")


@shared_task(bind=True, max_retries=3)
def send_feedback_request_email(self, appointment_id):
    """
    Send feedback request email after appointment is completed.
    
    Args:
        appointment_id: The ID of the completed appointment.
    """
    try:
        from apps.appointments.models import Appointment

        appointment = Appointment.objects.select_related(
            "customer", "barber", "barbershop"
        ).get(id=appointment_id)

        if not appointment.is_finished:
            return

        # Check if feedback already exists
        if hasattr(appointment, "feedback"):
            return

        subject = "How was your experience? - ApeX Barbershop"
        html_message = render_to_string(
            "emails/feedback_request.html",
            {
                "appointment": appointment,
                "customer": appointment.customer,
                "barber": appointment.barber,
                "barbershop": appointment.barbershop,
                "year": timezone.now().year,
            },
        )
        plain_message = (
            f"Hi {appointment.customer.first_name},\n\n"
            f"How was your appointment with {appointment.barber.full_name}?\n"
            f"We'd love to hear your feedback!\n"
        )

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.customer.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Feedback request email sent for appointment {appointment_id}")

    except Exception as e:
        logger.error(f"Failed to send feedback request email: {e}")
        raise self.retry(exc=e, countdown=60)
