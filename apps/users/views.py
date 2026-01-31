"""
Users app views.

Provides API views for user authentication and profile management.
"""

import logging

from django.contrib.auth import logout
from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.permissions import IsOwnerOrAdmin

from .models import User
from .serializers import (
    CustomTokenObtainPairSerializer,
    GoogleAuthSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserPublicSerializer,
    UserUpdateSerializer,
)

logger = logging.getLogger(__name__)


# ============== Authentication Views ==============


@extend_schema(tags=["auth"])
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    JWT token obtain view with custom serializer.
    
    Takes email and password, returns access and refresh tokens.
    """

    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(tags=["auth"])
class CustomTokenRefreshView(TokenRefreshView):
    """
    JWT token refresh view.
    
    Takes a refresh token, returns a new access token.
    """

    pass


@extend_schema(tags=["auth"])
class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    
    Creates a new user account and returns JWT tokens.
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create new user and return tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"New user registered: {user.email}")

        return Response(
            {
                "success": True,
                "message": "Registration successful.",
                "data": {
                    "user": UserDetailSerializer(user).data,
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                },
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["auth"])
class LoginView(APIView):
    """
    User login endpoint.
    
    Authenticates user with email/phone and password.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        """Authenticate user and return tokens."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"User logged in: {user.email}")

        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "data": {
                    "user": UserDetailSerializer(user).data,
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                },
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["auth"])
class LogoutView(APIView):
    """
    User logout endpoint.
    
    Blacklists the refresh token.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Logout user by blacklisting refresh token."""
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            logger.info(f"User logged out: {request.user.email}")
            
            return Response(
                {
                    "success": True,
                    "message": "Logout successful.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Invalid token.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(tags=["auth"])
class PasswordChangeView(APIView):
    """
    Password change endpoint.
    
    Changes the user's password after verifying current password.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        """Change user password."""
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()

        logger.info(f"Password changed for user: {request.user.email}")

        return Response(
            {
                "success": True,
                "message": "Password changed successfully.",
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["auth"])
class PasswordResetRequestView(APIView):
    """
    Password reset request endpoint.
    
    Sends a password reset email to the user.
    """

    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        """Send password reset email."""
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO: Implement password reset email sending via Celery
        logger.info(f"Password reset requested for: {serializer.validated_data['email']}")

        return Response(
            {
                "success": True,
                "message": "Password reset email sent.",
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["auth"])
class PasswordResetConfirmView(APIView):
    """
    Password reset confirmation endpoint.
    
    Resets the password using a token.
    """

    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        """Reset password with token."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO: Implement token validation and password reset

        return Response(
            {
                "success": True,
                "message": "Password reset successful.",
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["auth"])
class GoogleAuthView(APIView):
    """
    Google OAuth authentication endpoint.
    
    Authenticates user with Google access token.
    """

    permission_classes = [AllowAny]
    serializer_class = GoogleAuthSerializer

    def post(self, request):
        """Authenticate with Google OAuth."""
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO: Implement Google OAuth token validation
        # This would typically use social-auth-app-django

        return Response(
            {
                "success": True,
                "message": "Google authentication successful.",
            },
            status=status.HTTP_200_OK,
        )


# ============== User Profile Views ==============


@extend_schema(tags=["users"])
@extend_schema_view(
    list=extend_schema(description="List all users (admin only)"),
    retrieve=extend_schema(description="Get user details"),
    update=extend_schema(description="Update user profile"),
    partial_update=extend_schema(description="Partially update user profile"),
    destroy=extend_schema(description="Delete user account"),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management.
    
    Provides CRUD operations for users with role-based permissions.
    """

    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return UserListSerializer
        if self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        if self.action == "retrieve":
            # Check if viewing own profile or someone else's
            if self.kwargs.get("pk") == str(self.request.user.id):
                return UserDetailSerializer
            return UserPublicSerializer
        return UserDetailSerializer

    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action == "list":
            return [IsOwnerOrAdmin()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        if user.role in ["admin", "owner"]:
            return User.objects.all()
        # Regular users can only see their own profile
        return User.objects.filter(id=user.id)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """Delete user account."""
        instance = self.get_object()
        
        # Users can only delete their own account
        if instance != request.user and not request.user.role in ["admin", "owner"]:
            return Response(
                {
                    "success": False,
                    "message": "You can only delete your own account.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        logger.info(f"User account deleted: {instance.email}")
        self.perform_destroy(instance)

        return Response(
            {
                "success": True,
                "message": "Account deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user's profile."""
        serializer = UserDetailSerializer(request.user)
        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["put", "patch"])
    def update_me(self, request):
        """Update current user's profile."""
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Profile updated successfully.",
                "data": UserDetailSerializer(request.user).data,
            },
            status=status.HTTP_200_OK,
        )

