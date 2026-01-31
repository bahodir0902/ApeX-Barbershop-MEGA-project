"""
Custom exception handlers for ApeX Barbershop API.

Provides standardized error responses across all API endpoints.
"""

import logging

from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class BaseAPIException(APIException):
    """Base exception class for custom API exceptions."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "A server error occurred."
    default_code = "error"


class BadRequestException(BaseAPIException):
    """Exception for bad request errors (400)."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad request."
    default_code = "bad_request"


class UnauthorizedException(BaseAPIException):
    """Exception for unauthorized errors (401)."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication credentials were not provided."
    default_code = "not_authenticated"


class ForbiddenException(BaseAPIException):
    """Exception for forbidden errors (403)."""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to perform this action."
    default_code = "permission_denied"


class NotFoundException(BaseAPIException):
    """Exception for not found errors (404)."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found."
    default_code = "not_found"


class ConflictException(BaseAPIException):
    """Exception for conflict errors (409)."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "A conflict occurred."
    default_code = "conflict"


class UnprocessableEntityException(BaseAPIException):
    """Exception for unprocessable entity errors (422)."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Unable to process the request."
    default_code = "unprocessable_entity"


class ServiceUnavailableException(BaseAPIException):
    """Exception for service unavailable errors (503)."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Service temporarily unavailable."
    default_code = "service_unavailable"


def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent API error responses.
    
    Returns standardized error responses with the following structure:
    {
        "success": false,
        "error": {
            "code": "error_code",
            "message": "Error message",
            "details": {...} or null
        }
    }
    """
    # Get the standard DRF exception response
    response = exception_handler(exc, context)

    # Log the exception
    view = context.get("view", None)
    request = context.get("request", None)
    
    logger.error(
        "API Exception",
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "view": view.__class__.__name__ if view else None,
            "path": request.path if request else None,
            "method": request.method if request else None,
            "user": str(request.user) if request and hasattr(request, "user") else None,
        },
        exc_info=True,
    )

    if response is not None:
        # Customize the response format
        error_data = {
            "success": False,
            "error": {
                "code": getattr(exc, "default_code", "error"),
                "message": get_error_message(exc),
                "details": get_error_details(response.data),
            },
        }
        response.data = error_data
        return response

    # Handle Django exceptions that DRF doesn't handle
    if isinstance(exc, Http404):
        return Response(
            {
                "success": False,
                "error": {
                    "code": "not_found",
                    "message": "Resource not found.",
                    "details": None,
                },
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, PermissionDenied):
        return Response(
            {
                "success": False,
                "error": {
                    "code": "permission_denied",
                    "message": str(exc) or "Permission denied.",
                    "details": None,
                },
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, ValidationError):
        return Response(
            {
                "success": False,
                "error": {
                    "code": "validation_error",
                    "message": "Validation failed.",
                    "details": exc.message_dict if hasattr(exc, "message_dict") else str(exc),
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # For unhandled exceptions, return a generic error
    return Response(
        {
            "success": False,
            "error": {
                "code": "internal_error",
                "message": "An unexpected error occurred.",
                "details": None,
            },
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def get_error_message(exc):
    """Extract the primary error message from an exception."""
    if hasattr(exc, "detail"):
        detail = exc.detail
        if isinstance(detail, str):
            return detail
        if isinstance(detail, list) and len(detail) > 0:
            return str(detail[0])
        if isinstance(detail, dict):
            # Get the first error message
            for key, value in detail.items():
                if isinstance(value, list) and len(value) > 0:
                    return f"{key}: {value[0]}"
                return f"{key}: {value}"
    return str(exc)


def get_error_details(data):
    """Format error details from response data."""
    if isinstance(data, str):
        return None
    if isinstance(data, list):
        return {"errors": data} if len(data) > 1 else None
    if isinstance(data, dict):
        # Filter out the 'detail' key as it's already in the message
        details = {k: v for k, v in data.items() if k != "detail"}
        return details if details else None
    return None
