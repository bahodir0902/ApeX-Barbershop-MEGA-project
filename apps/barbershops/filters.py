"""
Barbershops app filters.

Provides advanced filtering for barbershops, barbers, and haircuts
using django-filter with trigram similarity search.
"""

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from django_filters import rest_framework as filters

from .models import Barber, Barbershop, Haircut


class BarbershopFilter(filters.FilterSet):
    """
    Filter for Barbershop model with advanced search capabilities.
    """

    name = filters.CharFilter(lookup_expr="icontains")
    address = filters.CharFilter(lookup_expr="icontains")
    search = filters.CharFilter(method="search_filter")
    is_active = filters.BooleanFilter()
    
    # Location-based filtering
    latitude = filters.NumberFilter()
    longitude = filters.NumberFilter()
    near = filters.CharFilter(method="near_filter")

    class Meta:
        model = Barbershop
        fields = ["name", "address", "is_active", "search"]

    def search_filter(self, queryset, name, value):
        """
        Search using trigram similarity for fuzzy matching.
        
        This enables typo-tolerant search across name and address.
        """
        if not value:
            return queryset

        # Use trigram similarity for fuzzy search
        return (
            queryset.annotate(
                name_similarity=TrigramSimilarity("name", value),
                address_similarity=TrigramSimilarity("address", value),
            )
            .filter(
                Q(name_similarity__gt=0.3)
                | Q(address_similarity__gt=0.3)
                | Q(name__icontains=value)
                | Q(address__icontains=value)
            )
            .order_by("-name_similarity", "-address_similarity")
        )

    def near_filter(self, queryset, name, value):
        """
        Filter barbershops near a location.
        
        Value format: "latitude,longitude,radius_km"
        Example: "41.3111,69.2797,5"
        """
        try:
            parts = value.split(",")
            if len(parts) >= 2:
                lat = float(parts[0])
                lng = float(parts[1])
                radius_km = float(parts[2]) if len(parts) > 2 else 10

                # Simple distance calculation (not accurate for large distances)
                # For production, consider using PostGIS
                lat_range = radius_km / 111  # 1 degree ≈ 111 km
                lng_range = radius_km / (111 * abs(lat) / 90 + 0.01)

                return queryset.filter(
                    latitude__range=(lat - lat_range, lat + lat_range),
                    longitude__range=(lng - lng_range, lng + lng_range),
                )
        except (ValueError, IndexError):
            pass
        return queryset


class BarberFilter(filters.FilterSet):
    """
    Filter for Barber model with advanced search capabilities.
    """

    name = filters.CharFilter(method="name_filter")
    search = filters.CharFilter(method="search_filter")
    barbershop = filters.UUIDFilter(field_name="barbershop__id")
    barbershop_name = filters.CharFilter(
        field_name="barbershop__name", lookup_expr="icontains"
    )
    is_active = filters.BooleanFilter()
    min_experience = filters.NumberFilter(
        field_name="experienced_years", lookup_expr="gte"
    )
    max_experience = filters.NumberFilter(
        field_name="experienced_years", lookup_expr="lte"
    )
    haircut = filters.UUIDFilter(method="haircut_filter")
    haircut_name = filters.CharFilter(method="haircut_name_filter")
    working_day = filters.CharFilter(method="working_day_filter")

    class Meta:
        model = Barber
        fields = ["barbershop", "is_active", "search"]

    def name_filter(self, queryset, name, value):
        """Filter by first name or last name."""
        return queryset.filter(
            Q(first_name__icontains=value) | Q(last_name__icontains=value)
        )

    def search_filter(self, queryset, name, value):
        """
        Search using trigram similarity for fuzzy matching.
        """
        if not value:
            return queryset

        return (
            queryset.annotate(
                first_name_similarity=TrigramSimilarity("first_name", value),
                last_name_similarity=TrigramSimilarity("last_name", value),
            )
            .filter(
                Q(first_name_similarity__gt=0.3)
                | Q(last_name_similarity__gt=0.3)
                | Q(first_name__icontains=value)
                | Q(last_name__icontains=value)
            )
            .order_by("-first_name_similarity", "-last_name_similarity")
        )

    def haircut_filter(self, queryset, name, value):
        """Filter barbers who can perform a specific haircut."""
        return queryset.filter(barber_haircuts__haircut__id=value)

    def haircut_name_filter(self, queryset, name, value):
        """Filter barbers who can perform haircuts matching name."""
        return queryset.filter(
            barber_haircuts__haircut__name__icontains=value
        ).distinct()

    def working_day_filter(self, queryset, name, value):
        """Filter barbers who work on a specific day."""
        return queryset.filter(working_days__icontains=value)


class HaircutFilter(filters.FilterSet):
    """
    Filter for Haircut model with advanced search capabilities.
    """

    name = filters.CharFilter(lookup_expr="icontains")
    search = filters.CharFilter(method="search_filter")
    barbershop = filters.UUIDFilter(field_name="barbershop__id")
    barbershop_name = filters.CharFilter(
        field_name="barbershop__name", lookup_expr="icontains"
    )
    is_active = filters.BooleanFilter()
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_duration = filters.NumberFilter(
        field_name="duration_minutes", lookup_expr="gte"
    )
    max_duration = filters.NumberFilter(
        field_name="duration_minutes", lookup_expr="lte"
    )
    barber = filters.UUIDFilter(method="barber_filter")

    class Meta:
        model = Haircut
        fields = ["barbershop", "is_active", "name", "search"]

    def search_filter(self, queryset, name, value):
        """
        Search using trigram similarity for fuzzy matching.
        """
        if not value:
            return queryset

        return (
            queryset.annotate(
                name_similarity=TrigramSimilarity("name", value),
                desc_similarity=TrigramSimilarity("description", value),
            )
            .filter(
                Q(name_similarity__gt=0.3)
                | Q(desc_similarity__gt=0.2)
                | Q(name__icontains=value)
                | Q(description__icontains=value)
            )
            .order_by("-name_similarity", "-desc_similarity")
        )

    def barber_filter(self, queryset, name, value):
        """Filter haircuts that a specific barber can perform."""
        return queryset.filter(barber_haircuts__barber__id=value)
