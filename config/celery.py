"""
Celery configuration for ApeX Barbershop API.

This module configures Celery for asynchronous task processing,
including email sending and scheduled tasks.
"""

import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("apex_barbershop")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    "send-appointment-reminders": {
        "task": "apps.appointments.tasks.send_appointment_reminders",
        "schedule": crontab(minute=0, hour="*/1"),  # Every hour
    },
    "cleanup-expired-tokens": {
        "task": "apps.users.tasks.cleanup_expired_tokens",
        "schedule": crontab(minute=0, hour=0),  # Daily at midnight
    },
    "generate-daily-reports": {
        "task": "apps.appointments.tasks.generate_daily_reports",
        "schedule": crontab(minute=0, hour=23),  # Daily at 11 PM
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f"Request: {self.request!r}")
