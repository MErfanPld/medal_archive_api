import django_filters
from django.db.models import Q

from .models import Medal


class MedalFilter(django_filters.FilterSet):
    """Advanced medal filters (exact + ranges + text search)."""

    search = django_filters.CharFilter(method='filter_search')
    country = django_filters.CharFilter(field_name='country', lookup_expr='iexact')
    country_contains = django_filters.CharFilter(field_name='country', lookup_expr='icontains')
    material = django_filters.CharFilter(field_name='material', lookup_expr='icontains')
    quality = django_filters.CharFilter(field_name='quality', lookup_expr='iexact')
    authenticity = django_filters.CharFilter(field_name='authenticity', lookup_expr='iexact')
    category = django_filters.NumberFilter(field_name='category_id')
    maker = django_filters.CharFilter(field_name='maker', lookup_expr='icontains')
    occasion = django_filters.CharFilter(field_name='occasion', lookup_expr='icontains')
    catalog_number = django_filters.CharFilter(field_name='catalog_number', lookup_expr='icontains')
    historical_period = django_filters.CharFilter(field_name='historical_period', lookup_expr='icontains')

    year = django_filters.NumberFilter(field_name='year')
    year_min = django_filters.NumberFilter(field_name='year', lookup_expr='gte')
    year_max = django_filters.NumberFilter(field_name='year', lookup_expr='lte')

    weight_min = django_filters.NumberFilter(field_name='weight', lookup_expr='gte')
    weight_max = django_filters.NumberFilter(field_name='weight', lookup_expr='lte')
    diameter_min = django_filters.NumberFilter(field_name='diameter', lookup_expr='gte')
    diameter_max = django_filters.NumberFilter(field_name='diameter', lookup_expr='lte')

    class Meta:
        model = Medal
        fields = []

    def filter_search(self, queryset, name, value):
        value = (value or '').strip()
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
            | Q(country__icontains=value)
            | Q(occasion__icontains=value)
            | Q(maker__icontains=value)
            | Q(mint_or_manufacturer__icontains=value)
            | Q(catalog_number__icontains=value)
            | Q(material__icontains=value)
            | Q(notes__icontains=value)
            | Q(historical_period__icontains=value)
        )
