"""
Core app views.

Provides health check and status endpoints.
"""

from django.db import connection
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring and load balancer health checks.
    
    Returns the health status of the application and its dependencies.
    """
    health_status = {
        "status": "healthy",
        "checks": {
            "database": check_database(),
            "cache": check_cache(),
        },
    }

    # Determine overall health
    all_healthy = all(
        check["status"] == "healthy" for check in health_status["checks"].values()
    )
    
    if not all_healthy:
        health_status["status"] = "unhealthy"
        return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response(health_status, status=status.HTTP_200_OK)


def check_database():
    """Check database connectivity."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}


def check_cache():
    """Check cache connectivity."""
    try:
        from django.core.cache import cache

        cache.set("health_check", "ok", 10)
        value = cache.get("health_check")
        if value == "ok":
            return {"status": "healthy", "message": "Cache connection successful"}
        return {"status": "unhealthy", "message": "Cache read/write failed"}
    except Exception as e:
        return {"status": "healthy", "message": f"Cache not configured: {e}"}


@api_view(["GET"])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Readiness check endpoint for Kubernetes.
    
    Indicates whether the application is ready to receive traffic.
    """
    return Response({"status": "ready"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def liveness_check(request):
    """
    Liveness check endpoint for Kubernetes.
    
    Indicates whether the application is running.
    """
    return Response({"status": "alive"}, status=status.HTTP_200_OK)

