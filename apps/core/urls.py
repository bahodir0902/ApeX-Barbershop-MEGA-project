"""
Core app URL patterns.

Provides health check endpoints.
"""

from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.health_check, name="health-check"),
    path("ready/", views.readiness_check, name="readiness-check"),
    path("live/", views.liveness_check, name="liveness-check"),
]
