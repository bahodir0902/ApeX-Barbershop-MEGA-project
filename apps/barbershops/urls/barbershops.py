"""
Barbershops URL patterns.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.barbershops.views import BarbershopViewSet

app_name = "barbershops"

router = DefaultRouter()
router.register("", BarbershopViewSet, basename="barbershop")

urlpatterns = [
    path("", include(router.urls)),
]
