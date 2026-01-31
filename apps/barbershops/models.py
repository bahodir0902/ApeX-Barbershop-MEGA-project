"""
Barbershops app models.

Defines models for Barbershop, Barber, and Haircut management.
"""

from datetime import time
from decimal import Decimal

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import BaseModel
from apps.users.models import User


class Barbershop(BaseModel):
    """
    Barbershop model representing a barbershop location.
    
    Stores information about barbershop name, address, contact details,
    and the owner of the barbershop.
    """

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="barbershops",
        limit_choices_to={"role__in": ["owner", "admin"]},
    )
    name = models.CharField(max_length=100, db_index=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    picture = models.ImageField(
        upload_to="barbershops/",
        blank=True,
        null=True,
    )
    description = models.TextField(blank=True, default="")
    
    # Location fields for geographical search
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )
    
    # Operating status
    is_active = models.BooleanField(default=True)
    
    # Search vector for full-text search
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        verbose_name = "Barbershop"
        verbose_name_plural = "Barbershops"
        ordering = ["name"]
        indexes = [
            GinIndex(fields=["search_vector"]),
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name

    @property
    def total_barbers(self):
        """Return the total number of barbers in this barbershop."""
        return self.barbers.count()

    @property
    def average_rating(self):
        """Calculate the average rating of all barbers in this barbershop."""
        from django.db.models import Avg

        avg = self.barbers.aggregate(avg_rating=Avg("feedbacks__rating"))
        return round(avg["avg_rating"] or 0, 1)


class Barber(BaseModel):
    """
    Barber model representing a barber working at a barbershop.
    
    Stores barber information including work schedule, experience,
    and links to the user account and barbershop.
    """

    # Link to user account (optional - barber may or may not have an account)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        related_name="barber_profile",
        null=True,
        blank=True,
        limit_choices_to={"role": "barber"},
    )
    
    # Barbershop association
    barbershop = models.ForeignKey(
        Barbershop,
        on_delete=models.CASCADE,
        related_name="barbers",
    )
    
    # Personal info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, default="")
    phone_number = models.CharField(max_length=30, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    picture = models.ImageField(
        upload_to="barbers/",
        blank=True,
        null=True,
    )
    
    # Professional info
    experienced_years = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True, default="")
    
    # Work schedule
    working_start_time = models.TimeField(default=time(9, 0))
    working_end_time = models.TimeField(default=time(18, 0))
    break_start_time = models.TimeField(default=time(12, 0))
    break_end_time = models.TimeField(default=time(13, 0))
    working_days = models.CharField(
        max_length=100,
        default="Monday, Tuesday, Wednesday, Thursday, Friday",
        help_text="Comma-separated list of working days",
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Search vector for full-text search
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        verbose_name = "Barber"
        verbose_name_plural = "Barbers"
        ordering = ["first_name", "last_name"]
        indexes = [
            GinIndex(fields=["search_vector"]),
            models.Index(fields=["first_name", "last_name"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.barbershop.name}"

    @property
    def full_name(self):
        """Return the barber's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def average_rating(self):
        """Calculate the average rating from feedbacks."""
        from django.db.models import Avg

        avg = self.feedbacks.aggregate(avg_rating=Avg("rating"))
        return round(avg["avg_rating"] or 0, 1)

    @property
    def total_appointments(self):
        """Return the total number of completed appointments."""
        return self.appointments.filter(is_finished=True).count()

    def get_working_days_list(self):
        """Return working days as a list."""
        return [day.strip() for day in self.working_days.split(",")]


class Haircut(BaseModel):
    """
    Haircut model representing a haircut service offered by a barbershop.
    
    Stores information about the haircut name, description, price,
    and duration.
    """

    barbershop = models.ForeignKey(
        Barbershop,
        on_delete=models.CASCADE,
        related_name="haircuts",
    )
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    picture = models.ImageField(
        upload_to="haircuts/",
        blank=True,
        null=True,
    )
    duration_minutes = models.PositiveIntegerField(
        default=45,
        validators=[MinValueValidator(5), MaxValueValidator(480)],
        help_text="Duration in minutes",
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Search vector for full-text search
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        verbose_name = "Haircut"
        verbose_name_plural = "Haircuts"
        ordering = ["name", "price"]
        indexes = [
            GinIndex(fields=["search_vector"]),
            models.Index(fields=["name"]),
            models.Index(fields=["price"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.price}"


class BarberHaircut(BaseModel):
    """
    Junction table linking barbers to haircuts they can perform.
    
    This allows different barbers to offer different services
    even within the same barbershop.
    """

    barber = models.ForeignKey(
        Barber,
        on_delete=models.CASCADE,
        related_name="barber_haircuts",
    )
    haircut = models.ForeignKey(
        Haircut,
        on_delete=models.CASCADE,
        related_name="barber_haircuts",
    )

    class Meta:
        verbose_name = "Barber Haircut"
        verbose_name_plural = "Barber Haircuts"
        unique_together = ["barber", "haircut"]
        ordering = ["barber", "haircut"]

    def __str__(self):
        return f"{self.barber.full_name} - {self.haircut.name}"

