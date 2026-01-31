"""
Barbershops app serializers.

Provides serializers for Barbershop, Barber, and Haircut models.
Serializers are separated by action for optimal performance.
"""

from django.db.models import Avg
from rest_framework import serializers

from apps.users.serializers import UserListSerializer

from .models import Barber, BarberHaircut, Barbershop, Haircut


# ============== Barbershop Serializers ==============


class BarbershopListSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for listing barbershops.
    """

    average_rating = serializers.FloatField(read_only=True)
    total_barbers = serializers.IntegerField(read_only=True)

    class Meta:
        model = Barbershop
        fields = [
            "id",
            "name",
            "address",
            "picture",
            "is_active",
            "average_rating",
            "total_barbers",
        ]
        read_only_fields = fields


class BarbershopDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for barbershop.
    """

    owner = UserListSerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    total_barbers = serializers.IntegerField(read_only=True)
    barbers = serializers.SerializerMethodField()
    haircuts = serializers.SerializerMethodField()

    class Meta:
        model = Barbershop
        fields = [
            "id",
            "name",
            "address",
            "phone_number",
            "picture",
            "description",
            "latitude",
            "longitude",
            "is_active",
            "owner",
            "average_rating",
            "total_barbers",
            "barbers",
            "haircuts",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "created_at",
            "updated_at",
        ]

    def get_barbers(self, obj):
        """Get active barbers for this barbershop."""
        barbers = obj.barbers.filter(is_active=True)[:5]
        return BarberListSerializer(barbers, many=True).data

    def get_haircuts(self, obj):
        """Get active haircuts for this barbershop."""
        haircuts = obj.haircuts.filter(is_active=True)[:5]
        return HaircutListSerializer(haircuts, many=True).data


class BarbershopCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a barbershop.
    """

    class Meta:
        model = Barbershop
        fields = [
            "name",
            "address",
            "phone_number",
            "picture",
            "description",
            "latitude",
            "longitude",
        ]

    def create(self, validated_data):
        """Create barbershop with current user as owner."""
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class BarbershopUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a barbershop.
    """

    class Meta:
        model = Barbershop
        fields = [
            "name",
            "address",
            "phone_number",
            "picture",
            "description",
            "latitude",
            "longitude",
            "is_active",
        ]


# ============== Barber Serializers ==============


class BarberListSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for listing barbers.
    """

    average_rating = serializers.FloatField(read_only=True)
    barbershop_name = serializers.CharField(source="barbershop.name", read_only=True)

    class Meta:
        model = Barber
        fields = [
            "id",
            "first_name",
            "last_name",
            "picture",
            "experienced_years",
            "average_rating",
            "barbershop_name",
            "is_active",
        ]
        read_only_fields = fields


class BarberDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for barber.
    """

    average_rating = serializers.FloatField(read_only=True)
    total_appointments = serializers.IntegerField(read_only=True)
    barbershop = BarbershopListSerializer(read_only=True)
    haircuts = serializers.SerializerMethodField()
    working_days_list = serializers.SerializerMethodField()
    user = UserListSerializer(read_only=True)

    class Meta:
        model = Barber
        fields = [
            "id",
            "user",
            "barbershop",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "picture",
            "bio",
            "experienced_years",
            "working_start_time",
            "working_end_time",
            "break_start_time",
            "break_end_time",
            "working_days",
            "working_days_list",
            "is_active",
            "average_rating",
            "total_appointments",
            "haircuts",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "average_rating",
            "total_appointments",
            "created_at",
            "updated_at",
        ]

    def get_haircuts(self, obj):
        """Get haircuts this barber can perform."""
        haircuts = Haircut.objects.filter(
            barber_haircuts__barber=obj, is_active=True
        )
        return HaircutListSerializer(haircuts, many=True).data

    def get_working_days_list(self, obj):
        """Get working days as a list."""
        return obj.get_working_days_list()


class BarberCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a barber.
    """

    barbershop_id = serializers.UUIDField(write_only=True)
    haircut_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Barber
        fields = [
            "barbershop_id",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "picture",
            "bio",
            "experienced_years",
            "working_start_time",
            "working_end_time",
            "break_start_time",
            "break_end_time",
            "working_days",
            "haircut_ids",
        ]

    def validate_barbershop_id(self, value):
        """Validate that barbershop exists and user has permission."""
        try:
            barbershop = Barbershop.objects.get(id=value)
            user = self.context["request"].user
            if barbershop.owner != user and user.role not in ["admin", "owner"]:
                raise serializers.ValidationError(
                    "You don't have permission to add barbers to this barbershop."
                )
            return value
        except Barbershop.DoesNotExist:
            raise serializers.ValidationError("Barbershop not found.")

    def create(self, validated_data):
        """Create barber and associate haircuts."""
        barbershop_id = validated_data.pop("barbershop_id")
        haircut_ids = validated_data.pop("haircut_ids", [])

        barbershop = Barbershop.objects.get(id=barbershop_id)
        barber = Barber.objects.create(barbershop=barbershop, **validated_data)

        # Associate haircuts
        for haircut_id in haircut_ids:
            try:
                haircut = Haircut.objects.get(id=haircut_id)
                BarberHaircut.objects.create(barber=barber, haircut=haircut)
            except Haircut.DoesNotExist:
                pass

        return barber


class BarberUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a barber.
    """

    haircut_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Barber
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "picture",
            "bio",
            "experienced_years",
            "working_start_time",
            "working_end_time",
            "break_start_time",
            "break_end_time",
            "working_days",
            "is_active",
            "haircut_ids",
        ]

    def update(self, instance, validated_data):
        """Update barber and haircut associations."""
        haircut_ids = validated_data.pop("haircut_ids", None)

        instance = super().update(instance, validated_data)

        if haircut_ids is not None:
            # Clear existing haircuts and add new ones
            instance.barber_haircuts.all().delete()
            for haircut_id in haircut_ids:
                try:
                    haircut = Haircut.objects.get(id=haircut_id)
                    BarberHaircut.objects.create(barber=instance, haircut=haircut)
                except Haircut.DoesNotExist:
                    pass

        return instance


class BarberScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for updating barber schedule only.
    """

    class Meta:
        model = Barber
        fields = [
            "working_start_time",
            "working_end_time",
            "break_start_time",
            "break_end_time",
            "working_days",
        ]


# ============== Haircut Serializers ==============


class HaircutListSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for listing haircuts.
    """

    barbershop_name = serializers.CharField(source="barbershop.name", read_only=True)

    class Meta:
        model = Haircut
        fields = [
            "id",
            "name",
            "price",
            "duration_minutes",
            "picture",
            "barbershop_name",
            "is_active",
        ]
        read_only_fields = fields


class HaircutDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for haircut.
    """

    barbershop = BarbershopListSerializer(read_only=True)
    barbers = serializers.SerializerMethodField()

    class Meta:
        model = Haircut
        fields = [
            "id",
            "barbershop",
            "name",
            "description",
            "price",
            "picture",
            "duration_minutes",
            "is_active",
            "barbers",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "barbershop",
            "created_at",
            "updated_at",
        ]

    def get_barbers(self, obj):
        """Get barbers who can perform this haircut."""
        barbers = Barber.objects.filter(
            barber_haircuts__haircut=obj, is_active=True
        )
        return BarberListSerializer(barbers, many=True).data


class HaircutCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a haircut.
    """

    barbershop_id = serializers.UUIDField(write_only=True)
    barber_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Haircut
        fields = [
            "barbershop_id",
            "name",
            "description",
            "price",
            "picture",
            "duration_minutes",
            "barber_ids",
        ]

    def validate_barbershop_id(self, value):
        """Validate that barbershop exists and user has permission."""
        try:
            barbershop = Barbershop.objects.get(id=value)
            user = self.context["request"].user
            if barbershop.owner != user and user.role not in ["admin", "owner"]:
                raise serializers.ValidationError(
                    "You don't have permission to add haircuts to this barbershop."
                )
            return value
        except Barbershop.DoesNotExist:
            raise serializers.ValidationError("Barbershop not found.")

    def create(self, validated_data):
        """Create haircut and associate barbers."""
        barbershop_id = validated_data.pop("barbershop_id")
        barber_ids = validated_data.pop("barber_ids", [])

        barbershop = Barbershop.objects.get(id=barbershop_id)
        haircut = Haircut.objects.create(barbershop=barbershop, **validated_data)

        # Associate barbers
        for barber_id in barber_ids:
            try:
                barber = Barber.objects.get(id=barber_id)
                BarberHaircut.objects.create(barber=barber, haircut=haircut)
            except Barber.DoesNotExist:
                pass

        return haircut


class HaircutUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a haircut.
    """

    barber_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Haircut
        fields = [
            "name",
            "description",
            "price",
            "picture",
            "duration_minutes",
            "is_active",
            "barber_ids",
        ]

    def update(self, instance, validated_data):
        """Update haircut and barber associations."""
        barber_ids = validated_data.pop("barber_ids", None)

        instance = super().update(instance, validated_data)

        if barber_ids is not None:
            # Clear existing barbers and add new ones
            instance.barber_haircuts.all().delete()
            for barber_id in barber_ids:
                try:
                    barber = Barber.objects.get(id=barber_id)
                    BarberHaircut.objects.create(barber=barber, haircut=instance)
                except Barber.DoesNotExist:
                    pass

        return instance
