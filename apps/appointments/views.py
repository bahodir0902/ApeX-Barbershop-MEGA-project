"""
Appointments app views.

Provides API views for Appointment and Feedback management.
"""

import logging

from django.db import transaction
from django.db.models import Avg, Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsBarberOrOwner, IsOwner

from .filters import AppointmentFilter, FeedbackFilter
from .models import Appointment, Feedback
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentDetailSerializer,
    AppointmentListSerializer,
    AppointmentStatusSerializer,
    AppointmentUpdateSerializer,
    FeedbackCreateSerializer,
    FeedbackDetailSerializer,
    FeedbackListSerializer,
    FeedbackResponseSerializer,
    FeedbackUpdateSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema(tags=["appointments"])
@extend_schema_view(
    list=extend_schema(description="List all appointments"),
    retrieve=extend_schema(description="Get appointment details"),
    create=extend_schema(description="Create a new appointment"),
    update=extend_schema(description="Update an appointment"),
    partial_update=extend_schema(description="Partially update an appointment"),
    destroy=extend_schema(description="Cancel an appointment"),
)
class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for appointment management.
    
    Provides CRUD operations for appointments with filtering.
    """

    queryset = Appointment.objects.all()
    serializer_class = AppointmentDetailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AppointmentFilter
    ordering_fields = ["appointment_date", "appointment_time", "created_at"]
    ordering = ["-appointment_date", "-appointment_time"]

    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = Appointment.objects.select_related(
            "barbershop", "barber", "customer", "haircut"
        ).prefetch_related("feedback")

        # Filter based on user role
        if user.role == "client":
            return queryset.filter(customer=user)
        elif user.role == "barber" and hasattr(user, "barber_profile"):
            return queryset.filter(barber=user.barber_profile)
        elif user.role in ["owner", "admin"]:
            return queryset
        return queryset.none()

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return AppointmentListSerializer
        if self.action == "create":
            return AppointmentCreateSerializer
        if self.action in ["update", "partial_update"]:
            return AppointmentUpdateSerializer
        if self.action == "update_status":
            return AppointmentStatusSerializer
        return AppointmentDetailSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        """Create appointment."""
        appointment = serializer.save()
        logger.info(
            f"Appointment created: {appointment.id} for "
            f"{appointment.customer.email} with {appointment.barber.full_name}"
        )

    def destroy(self, request, *args, **kwargs):
        """Cancel an appointment instead of deleting."""
        instance = self.get_object()

        # Check permission
        if instance.customer != request.user and request.user.role not in [
            "admin",
            "owner",
            "barber",
        ]:
            return Response(
                {"success": False, "message": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Don't allow cancelling completed appointments
        if instance.is_finished:
            return Response(
                {"success": False, "message": "Cannot cancel a completed appointment."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark as cancelled
        instance.mark_as_cancelled()
        logger.info(f"Appointment cancelled: {instance.id}")

        return Response(
            {
                "success": True,
                "message": "Appointment cancelled successfully.",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsBarberOrOwner])
    def complete(self, request, pk=None):
        """Mark an appointment as completed."""
        appointment = self.get_object()

        # Check permission for barbers
        if request.user.role == "barber":
            if (
                not hasattr(request.user, "barber_profile")
                or appointment.barber != request.user.barber_profile
            ):
                return Response(
                    {"success": False, "message": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if appointment.is_finished:
            return Response(
                {"success": False, "message": "Appointment is already completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.mark_as_completed()
        logger.info(f"Appointment completed: {appointment.id}")

        return Response(
            {
                "success": True,
                "message": "Appointment marked as completed.",
                "data": AppointmentDetailSerializer(appointment).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsBarberOrOwner])
    def update_status(self, request, pk=None):
        """Update appointment status."""
        appointment = self.get_object()

        serializer = AppointmentStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]
        appointment.status = new_status

        if new_status == Appointment.Status.COMPLETED:
            appointment.is_finished = True
        elif new_status == Appointment.Status.CANCELLED:
            appointment.is_active = False

        appointment.save()

        return Response(
            {
                "success": True,
                "message": f"Appointment status updated to {new_status}.",
                "data": AppointmentDetailSerializer(appointment).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def my_appointments(self, request):
        """Get current user's appointments."""
        queryset = self.get_queryset()
        
        # Apply filtering
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AppointmentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AppointmentListSerializer(queryset, many=True)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], permission_classes=[IsBarberOrOwner])
    def barber_appointments(self, request):
        """Get appointments for the current barber."""
        if not hasattr(request.user, "barber_profile"):
            return Response(
                {"success": False, "message": "You are not a barber."},
                status=status.HTTP_404_NOT_FOUND,
            )

        barber = request.user.barber_profile
        queryset = Appointment.objects.filter(barber=barber).select_related(
            "barbershop", "customer", "haircut"
        )

        # Apply date filter
        date_filter = request.query_params.get("date")
        if date_filter:
            queryset = queryset.filter(appointment_date=date_filter)

        # Apply status filter
        active_only = request.query_params.get("active_only", "false").lower() == "true"
        if active_only:
            queryset = queryset.filter(is_active=True, is_finished=False)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AppointmentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AppointmentListSerializer(queryset, many=True)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["feedbacks"])
@extend_schema_view(
    list=extend_schema(description="List all feedbacks"),
    retrieve=extend_schema(description="Get feedback details"),
    create=extend_schema(description="Create feedback for an appointment"),
    update=extend_schema(description="Update feedback"),
    partial_update=extend_schema(description="Partially update feedback"),
    destroy=extend_schema(description="Delete feedback"),
)
class FeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for feedback management.
    
    Provides CRUD operations for feedbacks with filtering.
    """

    queryset = Feedback.objects.all()
    serializer_class = FeedbackDetailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = FeedbackFilter
    ordering_fields = ["rating", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = Feedback.objects.select_related(
            "appointment", "barber", "customer"
        )

        # Clients see their own feedback
        if user.role == "client":
            return queryset.filter(customer=user)
        # Barbers see feedback for their appointments
        elif user.role == "barber" and hasattr(user, "barber_profile"):
            return queryset.filter(barber=user.barber_profile)
        # Owners and admins see all
        elif user.role in ["owner", "admin"]:
            return queryset
        return queryset.none()

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return FeedbackListSerializer
        if self.action == "create":
            return FeedbackCreateSerializer
        if self.action in ["update", "partial_update"]:
            return FeedbackUpdateSerializer
        if self.action == "respond":
            return FeedbackResponseSerializer
        return FeedbackDetailSerializer

    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action == "respond":
            return [IsBarberOrOwner()]
        return [IsAuthenticated()]

    @transaction.atomic
    def perform_create(self, serializer):
        """Create feedback."""
        feedback = serializer.save()
        logger.info(
            f"Feedback created: {feedback.id} - Rating: {feedback.rating}/5"
        )

    def destroy(self, request, *args, **kwargs):
        """Delete feedback (only owner can delete)."""
        instance = self.get_object()

        if instance.customer != request.user and request.user.role not in [
            "admin",
            "owner",
        ]:
            return Response(
                {"success": False, "message": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        self.perform_destroy(instance)
        logger.info(f"Feedback deleted: {instance.id}")

        return Response(
            {"success": True, "message": "Feedback deleted successfully."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsBarberOrOwner])
    def respond(self, request, pk=None):
        """Add barber response to feedback."""
        feedback = self.get_object()

        # Check permission for barbers
        if request.user.role == "barber":
            if (
                not hasattr(request.user, "barber_profile")
                or feedback.barber != request.user.barber_profile
            ):
                return Response(
                    {"success": False, "message": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        serializer = FeedbackResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        feedback.barber_response = serializer.validated_data["response"]
        feedback.response_date = timezone.now()
        feedback.save()

        return Response(
            {
                "success": True,
                "message": "Response added successfully.",
                "data": FeedbackDetailSerializer(feedback).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def barber_feedbacks(self, request):
        """Get feedbacks for a specific barber."""
        barber_id = request.query_params.get("barber_id")
        if not barber_id:
            return Response(
                {"success": False, "message": "barber_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = Feedback.objects.filter(barber_id=barber_id).select_related(
            "customer"
        )

        # Calculate statistics
        stats = queryset.aggregate(
            average_rating=Avg("rating"),
            total_reviews=Count("id"),
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FeedbackListSerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data["stats"] = stats
            return response

        serializer = FeedbackListSerializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "data": serializer.data,
                "stats": stats,
            },
            status=status.HTTP_200_OK,
        )

