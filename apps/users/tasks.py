"""
Celery tasks for Users app.

Provides asynchronous tasks for user-related operations.
"""

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, user_id):
    """
    Send welcome email to newly registered user.
    
    Args:
        user_id: The ID of the user to send the email to.
    """
    try:
        from apps.users.models import User

        user = User.objects.get(id=user_id)

        subject = "Welcome to ApeX Barbershop!"
        html_message = render_to_string(
            "emails/welcome.html",
            {
                "user": user,
                "year": timezone.now().year,
            },
        )
        plain_message = f"Welcome to ApeX Barbershop, {user.first_name}!"

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Welcome email sent to {user.email}")

    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_id, reset_token):
    """
    Send password reset email to user.
    
    Args:
        user_id: The ID of the user to send the email to.
        reset_token: The password reset token.
    """
    try:
        from apps.users.models import User

        user = User.objects.get(id=user_id)

        subject = "Password Reset Request - ApeX Barbershop"
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        html_message = render_to_string(
            "emails/password_reset.html",
            {
                "user": user,
                "reset_url": reset_url,
                "year": timezone.now().year,
            },
        )
        plain_message = f"Click here to reset your password: {reset_url}"

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Password reset email sent to {user.email}")

    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task
def cleanup_expired_tokens():
    """
    Clean up expired JWT tokens from the blacklist.
    
    This task runs daily to remove old blacklisted tokens.
    """
    try:
        from rest_framework_simplejwt.token_blacklist.models import (
            BlacklistedToken,
            OutstandingToken,
        )

        # Delete expired outstanding tokens
        expired_tokens = OutstandingToken.objects.filter(
            expires_at__lt=timezone.now()
        )
        count = expired_tokens.count()
        expired_tokens.delete()

        logger.info(f"Cleaned up {count} expired tokens")

    except Exception as e:
        logger.error(f"Failed to cleanup expired tokens: {e}")
