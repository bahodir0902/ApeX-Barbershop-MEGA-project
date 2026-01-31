"""
Barbers URL patterns.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.barbershops.views import BarberViewSet

app_name = "barbers"

router = DefaultRouter()
router.register("", BarberViewSet, basename="barber")

urlpatterns = [
    path("", include(router.urls)),
]
