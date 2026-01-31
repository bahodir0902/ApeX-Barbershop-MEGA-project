"""
Core app admin configuration.

Provides dashboard callbacks and environment indicators for Unfold admin.
"""

from django.contrib import admin

from apps.appointments.models import Appointment, Feedback
from apps.barbershops.models import Barber, Barbershop, Haircut
from apps.users.models import User


def environment_callback(request):
    """
    Return the current environment for display in admin header.
    
    Returns a tuple of (name, css_classes).
    """
    import os

    env = os.environ.get("DJANGO_ENV", "development")
    if env == "production":
        return "Production", "danger"
    if env == "staging":
        return "Staging", "warning"
    return "Development", "success"


def dashboard_callback(request, context):
    """
    Populate the admin dashboard with custom statistics and charts.
    
    This callback is used by Unfold to display custom dashboard content.
    """
    from datetime import timedelta

    from django.db.models import Avg, Count, Sum
    from django.db.models.functions import TruncDate, TruncMonth
    from django.utils import timezone

    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)

    # User statistics
    total_users = User.objects.count()
    new_users_30_days = User.objects.filter(created_at__date__gte=last_30_days).count()
    total_barbers = User.objects.filter(role="barber").count()
    total_clients = User.objects.filter(role="client").count()

    # Appointment statistics
    total_appointments = Appointment.objects.count()
    appointments_today = Appointment.objects.filter(appointment_date=today).count()
    appointments_this_week = Appointment.objects.filter(
        appointment_date__gte=last_7_days
    ).count()
    completed_appointments = Appointment.objects.filter(is_finished=True).count()
    active_appointments = Appointment.objects.filter(
        is_active=True, is_finished=False
    ).count()
    cancelled_appointments = Appointment.objects.filter(is_active=False).count()

    # Revenue statistics (assuming haircut prices)
    total_revenue = (
        Appointment.objects.filter(is_finished=True).aggregate(
            total=Sum("haircut__price")
        )["total"]
        or 0
    )
    revenue_this_month = (
        Appointment.objects.filter(
            is_finished=True,
            appointment_date__month=today.month,
            appointment_date__year=today.year,
        ).aggregate(total=Sum("haircut__price"))["total"]
        or 0
    )

    # Barbershop statistics
    total_barbershops = Barbershop.objects.count()
    total_haircuts = Haircut.objects.count()

    # Feedback statistics
    total_feedbacks = Feedback.objects.count()
    average_rating = Feedback.objects.aggregate(avg=Avg("rating"))["avg"] or 0

    # Chart data - Appointments per day (last 30 days)
    appointments_per_day = (
        Appointment.objects.filter(appointment_date__gte=last_30_days)
        .annotate(date=TruncDate("appointment_date"))
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    # Chart data - Revenue per month (last 6 months)
    six_months_ago = today - timedelta(days=180)
    revenue_per_month = (
        Appointment.objects.filter(
            is_finished=True, appointment_date__gte=six_months_ago
        )
        .annotate(month=TruncMonth("appointment_date"))
        .values("month")
        .annotate(revenue=Sum("haircut__price"))
        .order_by("month")
    )

    context.update(
        {
            # Statistics cards
            "stats": [
                {
                    "title": "Total Users",
                    "value": total_users,
                    "subtitle": f"+{new_users_30_days} last 30 days",
                    "icon": "people",
                },
                {
                    "title": "Barbers",
                    "value": total_barbers,
                    "subtitle": "Active barbers",
                    "icon": "content_cut",
                },
                {
                    "title": "Clients",
                    "value": total_clients,
                    "subtitle": "Registered clients",
                    "icon": "person",
                },
                {
                    "title": "Barbershops",
                    "value": total_barbershops,
                    "subtitle": "Active locations",
                    "icon": "store",
                },
                {
                    "title": "Appointments Today",
                    "value": appointments_today,
                    "subtitle": f"{active_appointments} active",
                    "icon": "calendar_today",
                },
                {
                    "title": "Appointments This Week",
                    "value": appointments_this_week,
                    "subtitle": f"{completed_appointments} completed total",
                    "icon": "event",
                },
                {
                    "title": "Total Revenue",
                    "value": f"${total_revenue:,.2f}",
                    "subtitle": f"${revenue_this_month:,.2f} this month",
                    "icon": "attach_money",
                },
                {
                    "title": "Average Rating",
                    "value": f"{average_rating:.1f}/5.0",
                    "subtitle": f"From {total_feedbacks} reviews",
                    "icon": "star",
                },
            ],
            # Chart data
            "appointments_chart_data": list(appointments_per_day),
            "revenue_chart_data": list(revenue_per_month),
            # Summary data
            "total_appointments": total_appointments,
            "cancelled_appointments": cancelled_appointments,
            "total_haircuts": total_haircuts,
        }
    )

    return context

