import django_filters

from .models import Stamp, AuthenticityStatus, ConditionGrade


class StampFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='country', lookup_expr='icontains')
    catalog_number = django_filters.CharFilter(field_name='catalog_number', lookup_expr='icontains')
    authenticity = django_filters.ChoiceFilter(choices=AuthenticityStatus.choices)
    condition = django_filters.ChoiceFilter(choices=ConditionGrade.choices)
    category = django_filters.NumberFilter(field_name='category_id')
    is_active = django_filters.BooleanFilter()
    year_min = django_filters.NumberFilter(field_name='year', lookup_expr='gte')
    year_max = django_filters.NumberFilter(field_name='year', lookup_expr='lte')
    current_value_min = django_filters.NumberFilter(field_name='current_value', lookup_expr='gte')
    current_value_max = django_filters.NumberFilter(field_name='current_value', lookup_expr='lte')
    is_used = django_filters.BooleanFilter()
    is_mint = django_filters.BooleanFilter()
    theme = django_filters.CharFilter(field_name='theme', lookup_expr='icontains')

    class Meta:
        model = Stamp
        fields = ['authenticity', 'condition', 'category', 'is_active', 'country', 'year']
