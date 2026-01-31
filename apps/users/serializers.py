"""
Users app serializers.

Provides serializers for user authentication and profile management.
Serializers are separated by action for optimal performance.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


# ============== Authentication Serializers ==============


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user information.
    """

    @classmethod
    def get_token(cls, user):
        """Add custom claims to the token."""
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        token["full_name"] = user.full_name
        return token

    def validate(self, attrs):
        """Validate and return tokens with user data."""
        data = super().validate(attrs)
        data["user"] = UserDetailSerializer(self.user).data
        return data


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login with email/phone and password.
    """

    email_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)
    remember = serializers.BooleanField(default=False, required=False)

    def validate(self, attrs):
        """Validate credentials and return user."""
        email_or_phone = attrs.get("email_or_phone")
        password = attrs.get("password")

        # Determine if it's email or phone
        if "@" in email_or_phone:
            user = User.objects.filter(email=email_or_phone).first()
        else:
            user = User.objects.filter(phone_number=email_or_phone).first()

        if not user:
            raise serializers.ValidationError(
                {"email_or_phone": "No user found with these credentials."}
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"password": "Incorrect password."}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"email_or_phone": "User account is disabled."}
            )

        attrs["user"] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    email_or_phone = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email_or_phone",
            "password",
            "password_confirm",
        ]

    def validate(self, attrs):
        """Validate registration data."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords don't match."}
            )

        email_or_phone = attrs.pop("email_or_phone")
        attrs.pop("password_confirm")

        # Determine if it's email or phone
        if "@" in email_or_phone:
            if User.objects.filter(email=email_or_phone).exists():
                raise serializers.ValidationError(
                    {"email_or_phone": "A user with this email already exists."}
                )
            attrs["email"] = email_or_phone
        else:
            if User.objects.filter(phone_number=email_or_phone).exists():
                raise serializers.ValidationError(
                    {"email_or_phone": "A user with this phone number already exists."}
                )
            attrs["phone_number"] = email_or_phone
            # Generate a placeholder email if only phone is provided
            attrs["email"] = f"{email_or_phone}@placeholder.local"

        return attrs

    def create(self, validated_data):
        """Create a new user."""
        user = User.objects.create_user(**validated_data)
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing password.
    """

    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_new_password = serializers.CharField(write_only=True, required=True)

    def validate_current_password(self, value):
        """Validate current password."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError(
                {"confirm_new_password": "New passwords don't match."}
            )
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset.
    """

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Validate that email exists."""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset.
    """

    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_new_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError(
                {"confirm_new_password": "Passwords don't match."}
            )
        return attrs


# ============== User Profile Serializers ==============


class UserListSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for listing users.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "profile_picture",
        ]
        read_only_fields = fields


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for user profile.
    """

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "privacy",
            "profile_picture",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "email",
            "role",
            "is_verified",
            "created_at",
            "updated_at",
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "privacy",
            "profile_picture",
        ]

    def validate_phone_number(self, value):
        """Validate phone number uniqueness."""
        user = self.instance
        if value and User.objects.filter(phone_number=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError(
                "A user with this phone number already exists."
            )
        return value


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Public serializer for viewing other users' profiles.
    Only shows public information.
    """

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "profile_picture",
        ]
        read_only_fields = fields


# ============== Social Auth Serializers ==============


class GoogleAuthSerializer(serializers.Serializer):
    """
    Serializer for Google OAuth authentication.
    """

    access_token = serializers.CharField(required=True)


class SocialAuthResponseSerializer(serializers.Serializer):
    """
    Response serializer for social authentication.
    """

    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserDetailSerializer()
