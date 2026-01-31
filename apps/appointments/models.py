"""
Appointments app models.

Defines models for Appointment and Feedback management.
"""

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.barbershops.models import Barber, Barbershop, Haircut
from apps.core.models import BaseModel
from apps.users.models import User


class Appointment(BaseModel):
    """
    Appointment model representing a booking for a haircut service.
    
    Stores information about the appointment including date, time,
    customer, barber, and status.
    """

    class Status(models.TextChoices):
        """Appointment status choices."""

        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    # Relations
    barbershop = models.ForeignKey(
        Barbershop,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    barber = models.ForeignKey(
        Barber,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointments",
        limit_choices_to={"role": "client"},
    )
    haircut = models.ForeignKey(
        Haircut,
        on_delete=models.CASCADE,
        related_name="appointments",
    )

    # Appointment details
    appointment_date = models.DateField(db_index=True)
    appointment_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=45)

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    is_active = models.BooleanField(default=True)
    is_finished = models.BooleanField(default=False)

    # Customer notes
    customer_notes = models.TextField(blank=True, default="")

    # Idempotency key to prevent duplicate bookings
    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
    )

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        ordering = ["-appointment_date", "-appointment_time"]
        indexes = [
            models.Index(fields=["appointment_date", "appointment_time"]),
            models.Index(fields=["barber", "appointment_date"]),
            models.Index(fields=["customer", "appointment_date"]),
            models.Index(fields=["status"]),
        ]
        # Prevent double booking
        constraints = [
            models.UniqueConstraint(
                fields=["barber", "appointment_date", "appointment_time"],
                condition=models.Q(is_active=True, is_finished=False),
                name="unique_barber_appointment_slot",
            ),
        ]

    def __str__(self):
        return (
            f"{self.customer.full_name} - {self.barber.full_name} - "
            f"{self.appointment_date} {self.appointment_time}"
        )

    @property
    def total_price(self):
        """Return the price of the haircut."""
        return self.haircut.price

    def mark_as_completed(self):
        """Mark the appointment as completed."""
        self.status = self.Status.COMPLETED
        self.is_finished = True
        self.save(update_fields=["status", "is_finished", "updated_at"])

    def mark_as_cancelled(self):
        """Mark the appointment as cancelled."""
        self.status = self.Status.CANCELLED
        self.is_active = False
        self.save(update_fields=["status", "is_active", "updated_at"])


class Feedback(BaseModel):
    """
    Feedback model representing customer reviews for appointments.
    
    Stores rating and comments from customers about their experience.
    """

    # Relations
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    barber = models.ForeignKey(
        Barber,
        on_delete=models.CASCADE,
        related_name="feedbacks",
    )
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="feedbacks",
        limit_choices_to={"role": "client"},
    )

    # Rating and comment
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0")), MaxValueValidator(Decimal("5.0"))],
        db_index=True,
    )
    comment = models.TextField(blank=True, default="")

    # Response from barber (optional)
    barber_response = models.TextField(blank=True, default="")
    response_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["barber", "rating"]),
            models.Index(fields=["customer"]),
        ]

    def __str__(self):
        return f"{self.customer.full_name} - {self.barber.full_name} - {self.rating}/5"

