"""
Barbershops app views.

Provides API views for Barbershop, Barber, and Haircut management.
"""

import logging
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Avg, Count, Prefetch
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsBarberOrOwner, IsOwnerOrAdmin

from .filters import BarberFilter, BarbershopFilter, HaircutFilter
from .models import Barber, BarberHaircut, Barbershop, Haircut
from .serializers import (
    BarberCreateSerializer,
    BarberDetailSerializer,
    BarberListSerializer,
    BarberScheduleSerializer,
    BarberUpdateSerializer,
    BarbershopCreateSerializer,
    BarbershopDetailSerializer,
    BarbershopListSerializer,
    BarbershopUpdateSerializer,
    HaircutCreateSerializer,
    HaircutDetailSerializer,
    HaircutListSerializer,
    HaircutUpdateSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema(tags=["barbershops"])
@extend_schema_view(
    list=extend_schema(description="List all barbershops"),
    retrieve=extend_schema(description="Get barbershop details"),
    create=extend_schema(description="Create a new barbershop"),
    update=extend_schema(description="Update a barbershop"),
    partial_update=extend_schema(description="Partially update a barbershop"),
    destroy=extend_schema(description="Delete a barbershop"),
)
class BarbershopViewSet(viewsets.ModelViewSet):
    """
    ViewSet for barbershop management.
    
    Provides CRUD operations for barbershops with filtering and search.
    """

    queryset = Barbershop.objects.all()
    serializer_class = BarbershopDetailSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BarbershopFilter
    search_fields = ["name", "address", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        """Optimize queryset with annotations and prefetching."""
        return (
            Barbershop.objects.annotate(
                _average_rating=Avg("barbers__feedbacks__rating"),
                _total_barbers=Count("barbers", distinct=True),
            )
            .select_related("owner")
            .prefetch_related(
                Prefetch(
                    "barbers",
                    queryset=Barber.objects.filter(is_active=True)[:5],
                ),
                Prefetch(
                    "haircuts",
                    queryset=Haircut.objects.filter(is_active=True)[:5],
                ),
            )
        )

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return BarbershopListSerializer
        if self.action == "create":
            return BarbershopCreateSerializer
        if self.action in ["update", "partial_update"]:
            return BarbershopUpdateSerializer
        return BarbershopDetailSerializer

    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsOwnerOrAdmin()]

    @transaction.atomic
    def perform_create(self, serializer):
        """Create barbershop with owner."""
        serializer.save(owner=self.request.user)
        logger.info(f"Barbershop created: {serializer.instance.name}")

    @action(detail=True, methods=["get"])
    def barbers(self, request, pk=None):
        """Get all barbers for this barbershop."""
        barbershop = self.get_object()
        barbers = Barber.objects.filter(
            barbershop=barbershop, is_active=True
        ).annotate(_average_rating=Avg("feedbacks__rating"))
        
        page = self.paginate_queryset(barbers)
        if page is not None:
            serializer = BarberListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BarberListSerializer(barbers, many=True)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def haircuts(self, request, pk=None):
        """Get all haircuts for this barbershop."""
        barbershop = self.get_object()
        haircuts = Haircut.objects.filter(barbershop=barbershop, is_active=True)
        
        page = self.paginate_queryset(haircuts)
        if page is not None:
            serializer = HaircutListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = HaircutListSerializer(haircuts, many=True)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["barbers"])
@extend_schema_view(
    list=extend_schema(description="List all barbers"),
    retrieve=extend_schema(description="Get barber details"),
    create=extend_schema(description="Create a new barber"),
    update=extend_schema(description="Update a barber"),
    partial_update=extend_schema(description="Partially update a barber"),
    destroy=extend_schema(description="Delete a barber"),
)
class BarberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for barber management.
    
    Provides CRUD operations for barbers with filtering and search.
    """

    queryset = Barber.objects.all()
    serializer_class = BarberDetailSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BarberFilter
    search_fields = ["first_name", "last_name", "bio"]
    ordering_fields = ["first_name", "last_name", "experienced_years", "created_at"]
    ordering = ["first_name", "last_name"]

    def get_queryset(self):
        """Optimize queryset with annotations and prefetching."""
        return (
            Barber.objects.annotate(
                _average_rating=Avg("feedbacks__rating"),
                _total_appointments=Count(
                    "appointments", filter=models.Q(appointments__is_finished=True)
                ),
            )
            .select_related("barbershop", "user")
            .prefetch_related("barber_haircuts__haircut")
        )

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return BarberListSerializer
        if self.action == "create":
            return BarberCreateSerializer
        if self.action in ["update", "partial_update"]:
            return BarberUpdateSerializer
        if self.action == "update_schedule":
            return BarberScheduleSerializer
        return BarberDetailSerializer

    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action in ["list", "retrieve", "available_slots"]:
            return [AllowAny()]
        if self.action in ["update_schedule", "my_appointments", "my_stats"]:
            return [IsBarberOrOwner()]
        return [IsOwnerOrAdmin()]

    @transaction.atomic
    def perform_create(self, serializer):
        """Create barber."""
        serializer.save()
        logger.info(f"Barber created: {serializer.instance.full_name}")

    @action(detail=True, methods=["get"])
    def available_slots(self, request, pk=None):
        """
        Get available appointment slots for a barber on a specific date.
        
        Query params:
            date: Date in YYYY-MM-DD format
        """
        barber = self.get_object()
        date_str = request.query_params.get("date")

        if not date_str:
            return Response(
                {"success": False, "message": "Date parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"success": False, "message": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if date is a working day
        day_name = date.strftime("%A")
        if day_name not in barber.get_working_days_list():
            return Response(
                {"success": True, "data": [], "message": "Barber is not working on this day."},
                status=status.HTTP_200_OK,
            )

        # Get booked slots
        from apps.appointments.models import Appointment

        booked_appointments = Appointment.objects.filter(
            barber=barber,
            appointment_date=date,
            is_active=True,
            is_finished=False,
        ).values_list("appointment_time", flat=True)

        booked_slots = set(booked_appointments)

        # Generate available slots
        available_slots = []
        current_time = datetime.combine(date, barber.working_start_time)
        end_time = datetime.combine(date, barber.working_end_time)
        break_start = datetime.combine(date, barber.break_start_time)
        break_end = datetime.combine(date, barber.break_end_time)

        slot_duration = timedelta(minutes=45)

        while current_time + slot_duration <= end_time:
            # Skip break time
            if break_start <= current_time < break_end:
                current_time = break_end
                continue

            slot_time = current_time.time()
            if slot_time not in booked_slots:
                available_slots.append(slot_time.strftime("%H:%M"))

            current_time += slot_duration

        return Response(
            {
                "success": True,
                "data": {
                    "date": date_str,
                    "barber": BarberListSerializer(barber).data,
                    "available_slots": available_slots,
                },
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def available_days(self, request, pk=None):
        """
        Get available days for a barber in the next 30 days.
        """
        barber = self.get_object()
        working_days = barber.get_working_days_list()

        today = timezone.now().date()
        available_dates = []

        for i in range(30):
            date = today + timedelta(days=i)
            day_name = date.strftime("%A")
            if day_name in working_days:
                available_dates.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "day": day_name,
                })

        return Response(
            {
                "success": True,
                "data": {
                    "barber": BarberListSerializer(barber).data,
                    "available_days": available_dates,
                },
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["put", "patch"])
    def update_schedule(self, request, pk=None):
        """Update barber's schedule."""
        barber = self.get_object()
        
        # Check permission
        if (
            request.user.role not in ["admin", "owner"]
            and (not hasattr(request.user, "barber_profile") or request.user.barber_profile != barber)
        ):
            return Response(
                {"success": False, "message": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = BarberScheduleSerializer(
            barber, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Schedule updated successfully.",
                "data": BarberDetailSerializer(barber).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user's barber profile."""
        if not hasattr(request.user, "barber_profile"):
            return Response(
                {"success": False, "message": "You are not a barber."},
                status=status.HTTP_404_NOT_FOUND,
            )

        barber = request.user.barber_profile
        serializer = BarberDetailSerializer(barber)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["haircuts"])
@extend_schema_view(
    list=extend_schema(description="List all haircuts"),
    retrieve=extend_schema(description="Get haircut details"),
    create=extend_schema(description="Create a new haircut"),
    update=extend_schema(description="Update a haircut"),
    partial_update=extend_schema(description="Partially update a haircut"),
    destroy=extend_schema(description="Delete a haircut"),
)
class HaircutViewSet(viewsets.ModelViewSet):
    """
    ViewSet for haircut management.
    
    Provides CRUD operations for haircuts with filtering and search.
    """

    queryset = Haircut.objects.all()
    serializer_class = HaircutDetailSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HaircutFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "price", "duration_minutes", "created_at"]
    ordering = ["name", "price"]

    def get_queryset(self):
        """Optimize queryset with prefetching."""
        return Haircut.objects.select_related("barbershop").prefetch_related(
            "barber_haircuts__barber"
        )

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return HaircutListSerializer
        if self.action == "create":
            return HaircutCreateSerializer
        if self.action in ["update", "partial_update"]:
            return HaircutUpdateSerializer
        return HaircutDetailSerializer

    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsBarberOrOwner()]

    @transaction.atomic
    def perform_create(self, serializer):
        """Create haircut."""
        serializer.save()
        logger.info(f"Haircut created: {serializer.instance.name}")

    @action(detail=True, methods=["get"])
    def barbers(self, request, pk=None):
        """Get all barbers who can perform this haircut."""
        haircut = self.get_object()
        barbers = Barber.objects.filter(
            barber_haircuts__haircut=haircut, is_active=True
        ).annotate(_average_rating=Avg("feedbacks__rating"))

        page = self.paginate_queryset(barbers)
        if page is not None:
            serializer = BarberListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BarberListSerializer(barbers, many=True)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )


# Import models for queryset annotation
from django.db import models

