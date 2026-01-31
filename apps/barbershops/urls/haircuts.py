"""
Haircuts URL patterns.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.barbershops.views import HaircutViewSet

app_name = "haircuts"

router = DefaultRouter()
router.register("", HaircutViewSet, basename="haircut")

urlpatterns = [
    path("", include(router.urls)),
]
