"""
Tests for Barbershop, Barber, and Haircut models and endpoints.
"""

from datetime import time
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from apps.barbershops.models import Barber, Barbershop, Haircut


@pytest.fixture
def barbershop(db, owner_user):
    """Create a test barbershop."""
    return Barbershop.objects.create(
        owner=owner_user,
        name="Test Barbershop",
        address="123 Test Street",
        phone_number="+1234567890",
        description="A test barbershop",
        is_active=True,
    )


@pytest.fixture
def barber(db, barbershop, barber_user):
    """Create a test barber."""
    barber = Barber.objects.create(
        user=barber_user,
        barbershop=barbershop,
        first_name="John",
        last_name="Barber",
        phone_number="+1234567891",
        email="john.barber@test.com",
        experienced_years=5,
        working_start_time=time(9, 0),
        working_end_time=time(18, 0),
        break_start_time=time(12, 0),
        break_end_time=time(13, 0),
        working_days="Monday, Tuesday, Wednesday, Thursday, Friday",
        is_active=True,
    )
    return barber


@pytest.fixture
def haircut(db, barbershop):
    """Create a test haircut."""
    return Haircut.objects.create(
        barbershop=barbershop,
        name="Classic Cut",
        description="A classic haircut",
        price=Decimal("25.00"),
        duration_minutes=30,
        is_active=True,
    )


@pytest.mark.django_db
class TestBarbershopModel:
    """Tests for the Barbershop model."""

    def test_create_barbershop(self, barbershop):
        """Test creating a barbershop."""
        assert barbershop.name == "Test Barbershop"
        assert barbershop.is_active is True
        assert str(barbershop) == "Test Barbershop"

    def test_barbershop_total_barbers(self, barbershop, barber):
        """Test total barbers property."""
        assert barbershop.total_barbers == 1


@pytest.mark.django_db
class TestBarberModel:
    """Tests for the Barber model."""

    def test_create_barber(self, barber):
        """Test creating a barber."""
        assert barber.first_name == "John"
        assert barber.experienced_years == 5
        assert barber.is_active is True

    def test_barber_full_name(self, barber):
        """Test barber full name property."""
        assert barber.full_name == "John Barber"

    def test_barber_working_days_list(self, barber):
        """Test getting working days as list."""
        days = barber.get_working_days_list()
        assert "Monday" in days
        assert "Saturday" not in days


@pytest.mark.django_db
class TestHaircutModel:
    """Tests for the Haircut model."""

    def test_create_haircut(self, haircut):
        """Test creating a haircut."""
        assert haircut.name == "Classic Cut"
        assert haircut.price == Decimal("25.00")
        assert haircut.duration_minutes == 30


@pytest.mark.django_db
class TestBarbershopEndpoints:
    """Tests for barbershop API endpoints."""

    def test_list_barbershops(self, api_client, barbershop):
        """Test listing barbershops."""
        url = reverse("barbershops:barbershop-list")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) >= 1

    def test_get_barbershop_detail(self, api_client, barbershop):
        """Test getting barbershop detail."""
        url = reverse("barbershops:barbershop-detail", kwargs={"pk": barbershop.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test Barbershop"

    def test_create_barbershop_as_owner(self, authenticated_owner_client):
        """Test creating a barbershop as owner."""
        url = reverse("barbershops:barbershop-list")
        data = {
            "name": "New Barbershop",
            "address": "456 New Street",
            "phone_number": "+9876543210",
        }
        response = authenticated_owner_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Barbershop.objects.filter(name="New Barbershop").exists()

    def test_create_barbershop_as_client_forbidden(self, authenticated_client):
        """Test that clients cannot create barbershops."""
        url = reverse("barbershops:barbershop-list")
        data = {
            "name": "New Barbershop",
            "address": "456 New Street",
        }
        response = authenticated_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_search_barbershops(self, api_client, barbershop):
        """Test searching barbershops."""
        url = reverse("barbershops:barbershop-list")
        response = api_client.get(url, {"search": "Test"})
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestBarberEndpoints:
    """Tests for barber API endpoints."""

    def test_list_barbers(self, api_client, barber):
        """Test listing barbers."""
        url = reverse("barbers:barber-list")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_barber_detail(self, api_client, barber):
        """Test getting barber detail."""
        url = reverse("barbers:barber-detail", kwargs={"pk": barber.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "John"

    def test_get_available_days(self, api_client, barber):
        """Test getting available days for a barber."""
        url = reverse("barbers:barber-available-days", kwargs={"pk": barber.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert "available_days" in response.data["data"]


@pytest.mark.django_db
class TestHaircutEndpoints:
    """Tests for haircut API endpoints."""

    def test_list_haircuts(self, api_client, haircut):
        """Test listing haircuts."""
        url = reverse("haircuts:haircut-list")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_haircut_detail(self, api_client, haircut):
        """Test getting haircut detail."""
        url = reverse("haircuts:haircut-detail", kwargs={"pk": haircut.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Classic Cut"

    def test_filter_haircuts_by_price(self, api_client, haircut):
        """Test filtering haircuts by price range."""
        url = reverse("haircuts:haircut-list")
        response = api_client.get(url, {"min_price": 20, "max_price": 30})
        
        assert response.status_code == status.HTTP_200_OK
