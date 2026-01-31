"""
Appointments app serializers.

Provides serializers for Appointment and Feedback models.
"""

from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.barbershops.models import Barber, Barbershop, Haircut
from apps.barbershops.serializers import (
    BarberListSerializer,
    BarbershopListSerializer,
    HaircutListSerializer,
)
from apps.users.serializers import UserListSerializer

from .models import Appointment, Feedback


# ============== Appointment Serializers ==============


class AppointmentListSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for listing appointments.
    """

    barbershop_name = serializers.CharField(source="barbershop.name", read_only=True)
    barber_name = serializers.CharField(source="barber.full_name", read_only=True)
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    haircut_name = serializers.CharField(source="haircut.name", read_only=True)
    haircut_price = serializers.DecimalField(
        source="haircut.price", max_digits=14, decimal_places=2, read_only=True
    )
    has_feedback = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id",
            "barbershop_name",
            "barber_name",
            "customer_name",
            "haircut_name",
            "haircut_price",
            "appointment_date",
            "appointment_time",
            "duration_minutes",
            "status",
            "is_active",
            "is_finished",
            "has_feedback",
        ]
        read_only_fields = fields

    def get_has_feedback(self, obj):
        """Check if feedback exists for this appointment."""
        return hasattr(obj, "feedback")


class AppointmentDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for appointment.
    """

    barbershop = BarbershopListSerializer(read_only=True)
    barber = BarberListSerializer(read_only=True)
    customer = UserListSerializer(read_only=True)
    haircut = HaircutListSerializer(read_only=True)
    feedback = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id",
            "barbershop",
            "barber",
            "customer",
            "haircut",
            "appointment_date",
            "appointment_time",
            "duration_minutes",
            "status",
            "is_active",
            "is_finished",
            "customer_notes",
            "feedback",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_feedback(self, obj):
        """Get feedback for this appointment if exists."""
        if hasattr(obj, "feedback"):
            return FeedbackListSerializer(obj.feedback).data
        return None


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating an appointment.
    
    Implements idempotent booking with conflict detection.
    """

    barbershop_id = serializers.UUIDField(write_only=True)
    barber_id = serializers.UUIDField(write_only=True)
    haircut_id = serializers.UUIDField(write_only=True)
    idempotency_key = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Appointment
        fields = [
            "barbershop_id",
            "barber_id",
            "haircut_id",
            "appointment_date",
            "appointment_time",
            "customer_notes",
            "idempotency_key",
        ]

    def validate(self, attrs):
        """Validate appointment data with conflict detection."""
        barbershop_id = attrs.get("barbershop_id")
        barber_id = attrs.get("barber_id")
        haircut_id = attrs.get("haircut_id")
        appointment_date = attrs.get("appointment_date")
        appointment_time = attrs.get("appointment_time")

        # Validate barbershop
        try:
            barbershop = Barbershop.objects.get(id=barbershop_id, is_active=True)
            attrs["barbershop"] = barbershop
        except Barbershop.DoesNotExist:
            raise serializers.ValidationError(
                {"barbershop_id": "Barbershop not found or inactive."}
            )

        # Validate barber
        try:
            barber = Barber.objects.get(
                id=barber_id, barbershop=barbershop, is_active=True
            )
            attrs["barber"] = barber
        except Barber.DoesNotExist:
            raise serializers.ValidationError(
                {"barber_id": "Barber not found or inactive."}
            )

        # Validate haircut
        try:
            haircut = Haircut.objects.get(
                id=haircut_id, barbershop=barbershop, is_active=True
            )
            attrs["haircut"] = haircut
        except Haircut.DoesNotExist:
            raise serializers.ValidationError(
                {"haircut_id": "Haircut not found or inactive."}
            )

        # Validate that barber can perform this haircut
        if not barber.barber_haircuts.filter(haircut=haircut).exists():
            raise serializers.ValidationError(
                {"haircut_id": "This barber does not offer this haircut."}
            )

        # Validate appointment is in the future
        appointment_datetime = datetime.combine(appointment_date, appointment_time)
        if appointment_datetime <= datetime.now():
            raise serializers.ValidationError(
                {"appointment_date": "Appointment must be in the future."}
            )

        # Validate appointment is on a working day
        day_name = appointment_date.strftime("%A")
        if day_name not in barber.get_working_days_list():
            raise serializers.ValidationError(
                {"appointment_date": f"Barber does not work on {day_name}."}
            )

        # Validate appointment time is within working hours
        if not (barber.working_start_time <= appointment_time <= barber.working_end_time):
            raise serializers.ValidationError(
                {"appointment_time": "Appointment time is outside working hours."}
            )

        # Validate appointment is not during break
        if barber.break_start_time <= appointment_time < barber.break_end_time:
            raise serializers.ValidationError(
                {"appointment_time": "Appointment time is during barber's break."}
            )

        # Check for existing appointments (conflict detection)
        existing = Appointment.objects.filter(
            barber=barber,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            is_active=True,
            is_finished=False,
        ).exists()

        if existing:
            raise serializers.ValidationError(
                {"appointment_time": "This time slot is already booked."}
            )

        # Check for customer's existing appointments at same time
        customer = self.context["request"].user
        customer_existing = Appointment.objects.filter(
            customer=customer,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            is_active=True,
            is_finished=False,
        ).exists()

        if customer_existing:
            raise serializers.ValidationError(
                {"appointment_time": "You already have an appointment at this time."}
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Create appointment with row locking for consistency."""
        # Remove IDs from validated data
        validated_data.pop("barbershop_id", None)
        validated_data.pop("barber_id", None)
        validated_data.pop("haircut_id", None)

        # Add customer and duration
        validated_data["customer"] = self.context["request"].user
        validated_data["duration_minutes"] = validated_data["haircut"].duration_minutes

        # Handle idempotency
        idempotency_key = validated_data.pop("idempotency_key", None)
        if idempotency_key:
            # Check for existing appointment with same key
            existing = Appointment.objects.filter(
                idempotency_key=idempotency_key
            ).first()
            if existing:
                return existing
            validated_data["idempotency_key"] = idempotency_key

        # Use select_for_update to lock the barber row
        barber = Barber.objects.select_for_update().get(id=validated_data["barber"].id)

        # Create appointment
        appointment = Appointment.objects.create(**validated_data)

        return appointment


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an appointment.
    """

    class Meta:
        model = Appointment
        fields = [
            "appointment_date",
            "appointment_time",
            "customer_notes",
        ]

    def validate(self, attrs):
        """Validate update data."""
        instance = self.instance
        appointment_date = attrs.get("appointment_date", instance.appointment_date)
        appointment_time = attrs.get("appointment_time", instance.appointment_time)

        # Validate appointment is in the future
        appointment_datetime = datetime.combine(appointment_date, appointment_time)
        if appointment_datetime <= datetime.now():
            raise serializers.ValidationError(
                {"appointment_date": "Appointment must be in the future."}
            )

        # Check for conflicts if date/time changed
        if (
            appointment_date != instance.appointment_date
            or appointment_time != instance.appointment_time
        ):
            existing = Appointment.objects.filter(
                barber=instance.barber,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                is_active=True,
                is_finished=False,
            ).exclude(id=instance.id).exists()

            if existing:
                raise serializers.ValidationError(
                    {"appointment_time": "This time slot is already booked."}
                )

        return attrs


class AppointmentStatusSerializer(serializers.Serializer):
    """
    Serializer for updating appointment status.
    """

    status = serializers.ChoiceField(choices=Appointment.Status.choices)


# ============== Feedback Serializers ==============


class FeedbackListSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for listing feedback.
    """

    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    barber_name = serializers.CharField(source="barber.full_name", read_only=True)

    class Meta:
        model = Feedback
        fields = [
            "id",
            "customer_name",
            "barber_name",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = fields


class FeedbackDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for feedback.
    """

    customer = UserListSerializer(read_only=True)
    barber = BarberListSerializer(read_only=True)
    appointment = AppointmentListSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = [
            "id",
            "appointment",
            "barber",
            "customer",
            "rating",
            "comment",
            "barber_response",
            "response_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class FeedbackCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating feedback.
    """

    appointment_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Feedback
        fields = [
            "appointment_id",
            "rating",
            "comment",
        ]

    def validate_appointment_id(self, value):
        """Validate that appointment exists and can receive feedback."""
        try:
            appointment = Appointment.objects.get(id=value)
        except Appointment.DoesNotExist:
            raise serializers.ValidationError("Appointment not found.")

        # Check if user owns the appointment
        user = self.context["request"].user
        if appointment.customer != user:
            raise serializers.ValidationError(
                "You can only leave feedback for your own appointments."
            )

        # Check if appointment is completed
        if not appointment.is_finished:
            raise serializers.ValidationError(
                "You can only leave feedback for completed appointments."
            )

        # Check if feedback already exists
        if hasattr(appointment, "feedback"):
            raise serializers.ValidationError(
                "Feedback already exists for this appointment."
            )

        return value

    def create(self, validated_data):
        """Create feedback."""
        appointment_id = validated_data.pop("appointment_id")
        appointment = Appointment.objects.get(id=appointment_id)

        return Feedback.objects.create(
            appointment=appointment,
            barber=appointment.barber,
            customer=self.context["request"].user,
            **validated_data,
        )


class FeedbackUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating feedback.
    """

    class Meta:
        model = Feedback
        fields = [
            "rating",
            "comment",
        ]


class FeedbackResponseSerializer(serializers.Serializer):
    """
    Serializer for barber response to feedback.
    """

    response = serializers.CharField(max_length=1000)
