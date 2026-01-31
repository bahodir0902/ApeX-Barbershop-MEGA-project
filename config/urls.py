"""
URL configuration for ApeX Barbershop API.

This module defines the main URL patterns for the API.
All API endpoints are prefixed with /api/v1/.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# API Version 1 URL patterns
api_v1_patterns = [
    path("auth/", include("apps.users.urls.auth")),
    path("users/", include("apps.users.urls.users")),
    path("barbershops/", include("apps.barbershops.urls.barbershops")),
    path("barbers/", include("apps.barbershops.urls.barbers")),
    path("haircuts/", include("apps.barbershops.urls.haircuts")),
    path("appointments/", include("apps.appointments.urls.appointments")),
    path("feedbacks/", include("apps.appointments.urls.feedbacks")),
]

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API v1
    path("api/v1/", include(api_v1_patterns)),
    # Social Auth
    path("auth/social/", include("social_django.urls", namespace="social")),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # Health check
    path("health/", include("apps.core.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
