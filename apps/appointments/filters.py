"""
Appointments app filters.

Provides advanced filtering for appointments and feedbacks.
"""

from django_filters import rest_framework as filters

from .models import Appointment, Feedback


class AppointmentFilter(filters.FilterSet):
    """
    Filter for Appointment model.
    """

    barbershop = filters.UUIDFilter(field_name="barbershop__id")
    barber = filters.UUIDFilter(field_name="barber__id")
    customer = filters.UUIDFilter(field_name="customer__id")
    haircut = filters.UUIDFilter(field_name="haircut__id")
    status = filters.ChoiceFilter(choices=Appointment.Status.choices)
    is_active = filters.BooleanFilter()
    is_finished = filters.BooleanFilter()
    date = filters.DateFilter(field_name="appointment_date")
    date_from = filters.DateFilter(field_name="appointment_date", lookup_expr="gte")
    date_to = filters.DateFilter(field_name="appointment_date", lookup_expr="lte")
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")

    class Meta:
        model = Appointment
        fields = [
            "barbershop",
            "barber",
            "customer",
            "haircut",
            "status",
            "is_active",
            "is_finished",
        ]


class FeedbackFilter(filters.FilterSet):
    """
    Filter for Feedback model.
    """

    barber = filters.UUIDFilter(field_name="barber__id")
    customer = filters.UUIDFilter(field_name="customer__id")
    appointment = filters.UUIDFilter(field_name="appointment__id")
    min_rating = filters.NumberFilter(field_name="rating", lookup_expr="gte")
    max_rating = filters.NumberFilter(field_name="rating", lookup_expr="lte")
    has_response = filters.BooleanFilter(method="filter_has_response")
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")

    class Meta:
        model = Feedback
        fields = [
            "barber",
            "customer",
            "appointment",
        ]

    def filter_has_response(self, queryset, name, value):
        """Filter feedbacks with or without barber response."""
        if value:
            return queryset.exclude(barber_response="")
        return queryset.filter(barber_response="")
