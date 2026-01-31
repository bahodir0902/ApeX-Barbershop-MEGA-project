"""
Tests for Appointment and Feedback models and endpoints.
"""

from datetime import date, time, timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.appointments.models import Appointment, Feedback
from apps.barbershops.models import Barber, BarberHaircut, Barbershop, Haircut


@pytest.fixture
def barbershop(db, owner_user):
    """Create a test barbershop."""
    return Barbershop.objects.create(
        owner=owner_user,
        name="Test Barbershop",
        address="123 Test Street",
        is_active=True,
    )


@pytest.fixture
def barber(db, barbershop, barber_user):
    """Create a test barber."""
    return Barber.objects.create(
        user=barber_user,
        barbershop=barbershop,
        first_name="John",
        last_name="Barber",
        working_start_time=time(9, 0),
        working_end_time=time(18, 0),
        break_start_time=time(12, 0),
        break_end_time=time(13, 0),
        working_days="Monday, Tuesday, Wednesday, Thursday, Friday, Saturday",
        is_active=True,
    )


@pytest.fixture
def haircut(db, barbershop):
    """Create a test haircut."""
    return Haircut.objects.create(
        barbershop=barbershop,
        name="Classic Cut",
        price=Decimal("25.00"),
        duration_minutes=45,
        is_active=True,
    )


@pytest.fixture
def barber_haircut(db, barber, haircut):
    """Link barber to haircut."""
    return BarberHaircut.objects.create(barber=barber, haircut=haircut)


@pytest.fixture
def appointment(db, barbershop, barber, haircut, client_user):
    """Create a test appointment."""
    tomorrow = date.today() + timedelta(days=1)
    return Appointment.objects.create(
        barbershop=barbershop,
        barber=barber,
        customer=client_user,
        haircut=haircut,
        appointment_date=tomorrow,
        appointment_time=time(10, 0),
        duration_minutes=45,
        status=Appointment.Status.CONFIRMED,
        is_active=True,
    )


@pytest.fixture
def completed_appointment(db, barbershop, barber, haircut, client_user):
    """Create a completed test appointment."""
    yesterday = date.today() - timedelta(days=1)
    return Appointment.objects.create(
        barbershop=barbershop,
        barber=barber,
        customer=client_user,
        haircut=haircut,
        appointment_date=yesterday,
        appointment_time=time(10, 0),
        duration_minutes=45,
        status=Appointment.Status.COMPLETED,
        is_active=True,
        is_finished=True,
    )


@pytest.mark.django_db
class TestAppointmentModel:
    """Tests for the Appointment model."""

    def test_create_appointment(self, appointment):
        """Test creating an appointment."""
        assert appointment.status == Appointment.Status.CONFIRMED
        assert appointment.is_active is True
        assert appointment.is_finished is False

    def test_appointment_total_price(self, appointment):
        """Test appointment total price property."""
        assert appointment.total_price == Decimal("25.00")

    def test_mark_as_completed(self, appointment):
        """Test marking appointment as completed."""
        appointment.mark_as_completed()
        
        assert appointment.status == Appointment.Status.COMPLETED
        assert appointment.is_finished is True

    def test_mark_as_cancelled(self, appointment):
        """Test marking appointment as cancelled."""
        appointment.mark_as_cancelled()
        
        assert appointment.status == Appointment.Status.CANCELLED
        assert appointment.is_active is False


@pytest.mark.django_db
class TestFeedbackModel:
    """Tests for the Feedback model."""

    def test_create_feedback(self, completed_appointment, client_user):
        """Test creating feedback."""
        feedback = Feedback.objects.create(
            appointment=completed_appointment,
            barber=completed_appointment.barber,
            customer=client_user,
            rating=Decimal("4.5"),
            comment="Great haircut!",
        )
        
        assert feedback.rating == Decimal("4.5")
        assert feedback.comment == "Great haircut!"


@pytest.mark.django_db
class TestAppointmentEndpoints:
    """Tests for appointment API endpoints."""

    def test_list_my_appointments(self, authenticated_client, appointment):
        """Test listing current user's appointments."""
        url = reverse("appointments:appointment-my-appointments")
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_appointment_detail(self, authenticated_client, appointment):
        """Test getting appointment detail."""
        url = reverse("appointments:appointment-detail", kwargs={"pk": appointment.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK

    def test_create_appointment(
        self, authenticated_client, barbershop, barber, haircut, barber_haircut
    ):
        """Test creating an appointment."""
        url = reverse("appointments:appointment-list")
        
        # Find a future working day
        future_date = date.today() + timedelta(days=1)
        while future_date.strftime("%A") not in barber.get_working_days_list():
            future_date += timedelta(days=1)
        
        data = {
            "barbershop_id": str(barbershop.id),
            "barber_id": str(barber.id),
            "haircut_id": str(haircut.id),
            "appointment_date": future_date.isoformat(),
            "appointment_time": "10:00",
            "customer_notes": "Please be gentle",
        }
        response = authenticated_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_appointment_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot create appointments."""
        url = reverse("appointments:appointment-list")
        response = api_client.post(url, {}, format="json")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cancel_appointment(self, authenticated_client, appointment):
        """Test cancelling an appointment."""
        url = reverse("appointments:appointment-detail", kwargs={"pk": appointment.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        appointment.refresh_from_db()
        assert appointment.status == Appointment.Status.CANCELLED

    def test_complete_appointment(self, authenticated_barber_client, appointment, barber_user):
        """Test completing an appointment as a barber."""
        # Link the appointment's barber to the barber user
        appointment.barber.user = barber_user
        appointment.barber.save()
        
        url = reverse("appointments:appointment-complete", kwargs={"pk": appointment.id})
        response = authenticated_barber_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestFeedbackEndpoints:
    """Tests for feedback API endpoints."""

    def test_create_feedback(self, authenticated_client, completed_appointment):
        """Test creating feedback for a completed appointment."""
        url = reverse("feedbacks:feedback-list")
        data = {
            "appointment_id": str(completed_appointment.id),
            "rating": "4.5",
            "comment": "Great service!",
        }
        response = authenticated_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_feedback_for_unfinished_appointment(
        self, authenticated_client, appointment
    ):
        """Test that feedback cannot be created for unfinished appointments."""
        url = reverse("feedbacks:feedback-list")
        data = {
            "appointment_id": str(appointment.id),
            "rating": "4.5",
            "comment": "Great service!",
        }
        response = authenticated_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_feedbacks(self, authenticated_client, completed_appointment, client_user):
        """Test listing feedbacks."""
        # Create a feedback first
        Feedback.objects.create(
            appointment=completed_appointment,
            barber=completed_appointment.barber,
            customer=client_user,
            rating=Decimal("4.5"),
            comment="Great!",
        )
        
        url = reverse("feedbacks:feedback-list")
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK

    def test_delete_own_feedback(self, authenticated_client, completed_appointment, client_user):
        """Test deleting own feedback."""
        feedback = Feedback.objects.create(
            appointment=completed_appointment,
            barber=completed_appointment.barber,
            customer=client_user,
            rating=Decimal("4.5"),
            comment="Great!",
        )
        
        url = reverse("feedbacks:feedback-detail", kwargs={"pk": feedback.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert not Feedback.objects.filter(id=feedback.id).exists()
