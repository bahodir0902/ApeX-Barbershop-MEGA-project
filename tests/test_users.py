"""
Tests for User model and authentication endpoints.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Tests for the User model."""

    def test_create_user(self, user_factory):
        """Test creating a user."""
        user = user_factory()
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.role == "client"
        assert user.is_active is True
        assert user.is_staff is False

    def test_create_user_with_different_roles(self, user_factory):
        """Test creating users with different roles."""
        client = user_factory(email="client@test.com", role="client")
        barber = user_factory(email="barber@test.com", role="barber")
        owner = user_factory(email="owner@test.com", role="owner")

        assert client.is_client is True
        assert barber.is_barber is True
        assert owner.is_owner is True

    def test_user_full_name(self, user_factory):
        """Test user full name property."""
        user = user_factory(first_name="John", last_name="Doe")
        assert user.full_name == "John Doe"

    def test_user_str_representation(self, user_factory):
        """Test user string representation."""
        user = user_factory()
        assert str(user) == "Test User (test@example.com)"


@pytest.mark.django_db
class TestAuthenticationEndpoints:
    """Tests for authentication API endpoints."""

    def test_register_user(self, api_client):
        """Test user registration."""
        url = reverse("auth:register")
        data = {
            "email_or_phone": "newuser@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "New",
            "last_name": "User",
        }
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert "tokens" in response.data["data"]
        assert User.objects.filter(email="newuser@example.com").exists()

    def test_register_user_password_mismatch(self, api_client):
        """Test registration fails with password mismatch."""
        url = reverse("auth:register")
        data = {
            "email_or_phone": "newuser@example.com",
            "password": "SecurePass123!",
            "password_confirm": "DifferentPass123!",
            "first_name": "New",
        }
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_email(self, api_client, client_user):
        """Test login with email."""
        url = reverse("auth:login")
        data = {
            "email_or_phone": client_user.email,
            "password": "testpass123",
        }
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        assert "tokens" in response.data["data"]

    def test_login_with_wrong_password(self, api_client, client_user):
        """Test login fails with wrong password."""
        url = reverse("auth:login")
        data = {
            "email_or_phone": client_user.email,
            "password": "wrongpassword",
        }
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout(self, authenticated_client):
        """Test logout endpoint."""
        url = reverse("auth:logout")
        response = authenticated_client.post(url, {}, format="json")
        
        assert response.status_code == status.HTTP_200_OK

    def test_token_refresh(self, api_client, client_user):
        """Test token refresh."""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh = RefreshToken.for_user(client_user)
        url = reverse("auth:token-refresh")
        response = api_client.post(url, {"refresh": str(refresh)}, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data


@pytest.mark.django_db
class TestUserEndpoints:
    """Tests for user management endpoints."""

    def test_get_current_user(self, authenticated_client, client_user):
        """Test getting current user profile."""
        url = reverse("users:user-me")
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["email"] == client_user.email

    def test_update_profile(self, authenticated_client, client_user):
        """Test updating user profile."""
        url = reverse("users:user-update-me")
        data = {"first_name": "Updated"}
        response = authenticated_client.patch(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        
        client_user.refresh_from_db()
        assert client_user.first_name == "Updated"

    def test_password_change(self, authenticated_client, client_user):
        """Test password change."""
        url = reverse("auth:password-change")
        data = {
            "current_password": "testpass123",
            "new_password": "NewSecurePass123!",
            "confirm_new_password": "NewSecurePass123!",
        }
        response = authenticated_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        
        client_user.refresh_from_db()
        assert client_user.check_password("NewSecurePass123!")

    def test_unauthenticated_access(self, api_client):
        """Test that unauthenticated users cannot access protected endpoints."""
        url = reverse("users:user-me")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
