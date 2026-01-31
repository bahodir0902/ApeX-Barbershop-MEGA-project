"""
Authentication URL patterns for Users app.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from apps.users.views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    GoogleAuthView,
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
)

app_name = "auth"

urlpatterns = [
    # JWT Token endpoints
    path("token/", CustomTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    # Registration and Login
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # Password management
    path("password/change/", PasswordChangeView.as_view(), name="password-change"),
    path(
        "password/reset/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    # Social Auth
    path("google/", GoogleAuthView.as_view(), name="google-auth"),
]
