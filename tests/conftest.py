"""
Pytest configuration and fixtures for ApeX Barbershop API tests.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an API client instance."""
    return APIClient()


@pytest.fixture
def user_factory(db):
    """Factory for creating test users."""
    def create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
        role="client",
        is_active=True,
        **kwargs
    ):
        return User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_active=is_active,
            **kwargs
        )
    return create_user


@pytest.fixture
def client_user(user_factory):
    """Create a client user."""
    return user_factory(
        email="client@example.com",
        role="client",
    )


@pytest.fixture
def barber_user(user_factory):
    """Create a barber user."""
    return user_factory(
        email="barber@example.com",
        role="barber",
    )


@pytest.fixture
def owner_user(user_factory):
    """Create an owner user."""
    return user_factory(
        email="owner@example.com",
        role="owner",
    )


@pytest.fixture
def admin_user(user_factory):
    """Create an admin user."""
    return user_factory(
        email="admin@example.com",
        role="admin",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def authenticated_client(api_client, client_user):
    """Return an authenticated API client for a client user."""
    refresh = RefreshToken.for_user(client_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def authenticated_barber_client(api_client, barber_user):
    """Return an authenticated API client for a barber user."""
    refresh = RefreshToken.for_user(barber_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def authenticated_owner_client(api_client, owner_user):
    """Return an authenticated API client for an owner user."""
    refresh = RefreshToken.for_user(owner_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    """Return an authenticated API client for an admin user."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client
