"""
Core app base models.

Provides abstract base models with common fields for all models.
"""

import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides created_at and updated_at timestamps.
    
    All models should inherit from this to ensure consistent timestamp tracking.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class UUIDModel(models.Model):
    """
    Abstract base model that provides a UUID primary key.
    
    Use this for models that require UUID-based identification
    for better security and distributed systems compatibility.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, UUIDModel):
    """
    Abstract base model combining UUID primary key and timestamps.
    
    This is the recommended base model for most application models.
    """

    class Meta:
        abstract = True
        ordering = ["-created_at"]

