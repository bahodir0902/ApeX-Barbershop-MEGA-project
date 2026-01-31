"""
Users app models.

Defines the custom User model with role-based access control.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models

from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    """Custom user manager for User model."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom User model with role-based access control.
    
    Supports three roles:
    - client: Regular customers who book appointments
    - barber: Barbers who provide services
    - owner: Barbershop owners with admin privileges
    - admin: System administrators
    """

    class Role(models.TextChoices):
        """User role choices."""

        CLIENT = "client", "Client"
        BARBER = "barber", "Barber"
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"

    class Privacy(models.TextChoices):
        """Profile privacy choices."""

        PRIVATE = "private", "Private"
        PUBLIC = "public", "Public"

    # Basic info
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=30, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, default="")

    # Role and permissions
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
        db_index=True,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    # Privacy settings
    privacy = models.CharField(
        max_length=20,
        choices=Privacy.choices,
        default=Privacy.PRIVATE,
    )

    # Profile
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
    )
    
    # Search vector for full-text search
    search_vector = SearchVectorField(null=True, blank=True)

    # Manager
    objects = UserManager()

    # Auth settings
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]
        indexes = [
            GinIndex(fields=["search_vector"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_owner(self):
        """Check if user is an owner."""
        return self.role == self.Role.OWNER

    @property
    def is_barber(self):
        """Check if user is a barber."""
        return self.role == self.Role.BARBER

    @property
    def is_client(self):
        """Check if user is a client."""
        return self.role == self.Role.CLIENT

    @property
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == self.Role.ADMIN

