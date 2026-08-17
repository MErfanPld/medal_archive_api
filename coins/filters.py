import django_filters

from .models import AuthenticityStatus, Coin, ItemType, QualityGrade


class CoinFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='country', lookup_expr='iexact')
    country_contains = django_filters.CharFilter(field_name='country', lookup_expr='icontains')
    material = django_filters.CharFilter(field_name='material', lookup_expr='icontains')
    catalog_number = django_filters.CharFilter(field_name='catalog_number', lookup_expr='icontains')
    denomination = django_filters.CharFilter(field_name='denomination', lookup_expr='icontains')
    serial_number = django_filters.CharFilter(field_name='serial_number', lookup_expr='icontains')
    historical_period = django_filters.CharFilter(field_name='historical_period', lookup_expr='icontains')
    mint = django_filters.CharFilter(field_name='mint', lookup_expr='icontains')

    item_type = django_filters.ChoiceFilter(choices=ItemType.choices)
    quality = django_filters.ChoiceFilter(choices=QualityGrade.choices)
    authenticity = django_filters.ChoiceFilter(choices=AuthenticityStatus.choices)
    category = django_filters.NumberFilter(field_name='category_id')
    is_active = django_filters.BooleanFilter()
    is_proof = django_filters.BooleanFilter()
    is_commemorative = django_filters.BooleanFilter()

    year_min = django_filters.NumberFilter(field_name='year', lookup_expr='gte')
    year_max = django_filters.NumberFilter(field_name='year', lookup_expr='lte')
    face_value_min = django_filters.NumberFilter(field_name='face_value', lookup_expr='gte')
    face_value_max = django_filters.NumberFilter(field_name='face_value', lookup_expr='lte')
    weight_min = django_filters.NumberFilter(field_name='weight', lookup_expr='gte')
    weight_max = django_filters.NumberFilter(field_name='weight', lookup_expr='lte')
    current_value_min = django_filters.NumberFilter(field_name='current_value', lookup_expr='gte')
    current_value_max = django_filters.NumberFilter(field_name='current_value', lookup_expr='lte')

    class Meta:
        model = Coin
        fields = [
            'item_type', 'quality', 'authenticity', 'category', 'is_active',
            'is_proof', 'is_commemorative', 'country', 'year',
        ]
