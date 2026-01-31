"""
Core app permissions.

Provides custom permission classes for role-based access control.
"""

from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """
    Permission that allows only owners or admins.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["owner", "admin"]
        )


class IsBarber(BasePermission):
    """
    Permission that allows only barbers.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "barber"
        )


class IsClient(BasePermission):
    """
    Permission that allows only clients.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "client"
        )


class IsBarberOrOwner(BasePermission):
    """
    Permission that allows barbers or owners/admins.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["barber", "owner", "admin"]
        )


class IsOwner(BasePermission):
    """
    Object-level permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the object has an owner field
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "customer"):
            return obj.customer == request.user
        return False


class IsBarberOfObject(BasePermission):
    """
    Object-level permission to only allow barbers assigned to an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "barber"):
            if hasattr(request.user, "barber_profile"):
                return obj.barber == request.user.barber_profile
        return False


class ReadOnly(BasePermission):
    """
    Permission that allows read-only access to all users.
    """

    def has_permission(self, request, view):
        return request.method in ["GET", "HEAD", "OPTIONS"]


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Permission that allows authenticated users full access,
    or read-only access for unauthenticated users.
    """

    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return request.user and request.user.is_authenticated
