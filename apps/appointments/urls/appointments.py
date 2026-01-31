"""
Appointments URL patterns.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.appointments.views import AppointmentViewSet

app_name = "appointments"

router = DefaultRouter()
router.register("", AppointmentViewSet, basename="appointment")

urlpatterns = [
    path("", include(router.urls)),
]
