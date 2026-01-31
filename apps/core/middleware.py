"""
Custom middleware for ApeX Barbershop API.

Provides request logging and other cross-cutting concerns.
"""

import logging
import time
import uuid

from django.conf import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Middleware for logging all HTTP requests and responses.
    
    Logs request details, response status, and timing information
    in a structured format for monitoring and debugging.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate a unique request ID
        request_id = str(uuid.uuid4())[:8]
        request.request_id = request_id

        # Record start time
        start_time = time.time()

        # Get user info
        user = getattr(request, "user", None)
        user_id = getattr(user, "id", None) if user and user.is_authenticated else None

        # Log the incoming request
        logger.info(
            "Request received",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "query_params": dict(request.GET),
                "user_id": str(user_id) if user_id else None,
                "ip_address": self.get_client_ip(request),
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            },
        )

        # Process the request
        response = self.get_response(request)

        # Calculate request duration
        duration = time.time() - start_time

        # Log the response
        log_level = logging.INFO if response.status_code < 400 else logging.WARNING
        if response.status_code >= 500:
            log_level = logging.ERROR

        logger.log(
            log_level,
            "Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "user_id": str(user_id) if user_id else None,
            },
        )

        # Add request ID to response headers
        response["X-Request-ID"] = request_id
        response["X-Response-Time"] = f"{round(duration * 1000, 2)}ms"

        return response

    @staticmethod
    def get_client_ip(request):
        """Extract the client IP address from the request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class IdempotencyMiddleware:
    """
    Middleware for handling idempotent requests.
    
    Uses an Idempotency-Key header to ensure that requests
    with the same key return the same response.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.cache = None

    def __call__(self, request):
        # Only apply to POST, PUT, PATCH requests
        if request.method not in ["POST", "PUT", "PATCH"]:
            return self.get_response(request)

        # Get idempotency key from header
        idempotency_key = request.META.get("HTTP_IDEMPOTENCY_KEY")
        if not idempotency_key:
            return self.get_response(request)

        # Try to get cached response
        from django.core.cache import cache

        cache_key = f"idempotency:{idempotency_key}"
        cached_response = cache.get(cache_key)

        if cached_response:
            logger.info(
                "Returning cached idempotent response",
                extra={
                    "idempotency_key": idempotency_key,
                    "path": request.path,
                },
            )
            from django.http import JsonResponse

            return JsonResponse(
                cached_response["data"],
                status=cached_response["status"],
            )

        # Process the request
        response = self.get_response(request)

        # Cache the response for idempotent replay
        if 200 <= response.status_code < 300:
            try:
                import json

                response_data = json.loads(response.content.decode("utf-8"))
                cache.set(
                    cache_key,
                    {
                        "data": response_data,
                        "status": response.status_code,
                    },
                    timeout=86400,  # 24 hours
                )
            except (json.JSONDecodeError, AttributeError):
                pass

        return response


class CORSDebugMiddleware:
    """
    Debug middleware for CORS issues in development.
    
    Only active when DEBUG is True.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if settings.DEBUG and request.method == "OPTIONS":
            logger.debug(
                "CORS preflight request",
                extra={
                    "origin": request.META.get("HTTP_ORIGIN"),
                    "access_control_request_method": request.META.get(
                        "HTTP_ACCESS_CONTROL_REQUEST_METHOD"
                    ),
                    "access_control_request_headers": request.META.get(
                        "HTTP_ACCESS_CONTROL_REQUEST_HEADERS"
                    ),
                },
            )

        return response
