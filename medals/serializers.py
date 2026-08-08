from datetime import date

from rest_framework import serializers

from categories.serializers import CategorySerializer

from .models import Medal


class MedalSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Medal
        fields = [
            'id', 'name', 'country', 'year', 'occasion', 'historical_period',
            'maker', 'mint_or_manufacturer', 'category', 'category_detail',
            'material', 'weight', 'diameter', 'thickness', 'shape', 'color', 'edge',
            'quality', 'preservation_condition', 'authenticity', 'catalog_number',
            'purchase_date', 'purchase_location', 'seller',
            'purchase_price', 'purchase_currency',
            'current_value', 'last_valuation_date',
            'cabinet_number', 'drawer_number', 'box_number',
            'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'category_detail']

    def validate_name(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Name is required.')
        return value

    def validate_year(self, value):
        if value is None:
            return value
        current = date.today().year
        if value < 1 or value > current + 1:
            raise serializers.ValidationError(f'Year must be between 1 and {current + 1}.')
        return value

    def _validate_non_negative(self, value, field_name):
        if value is not None and value < 0:
            raise serializers.ValidationError(f'{field_name} cannot be negative.')
        return value

    def validate_weight(self, value):
        return self._validate_non_negative(value, 'Weight')

    def validate_diameter(self, value):
        return self._validate_non_negative(value, 'Diameter')

    def validate_thickness(self, value):
        return self._validate_non_negative(value, 'Thickness')

    def validate_purchase_price(self, value):
        return self._validate_non_negative(value, 'Purchase price')

    def validate_current_value(self, value):
        return self._validate_non_negative(value, 'Current value')

    def validate_category(self, value):
        if value is not None and not value.is_active:
            raise serializers.ValidationError('Cannot assign an inactive category.')
        return value

    def validate(self, attrs):
        purchase_date = attrs.get('purchase_date', getattr(self.instance, 'purchase_date', None))
        last_valuation_date = attrs.get(
            'last_valuation_date', getattr(self.instance, 'last_valuation_date', None)
        )
        today = date.today()
        if purchase_date and purchase_date > today:
            raise serializers.ValidationError({'purchase_date': 'Purchase date cannot be in the future.'})
        if last_valuation_date and last_valuation_date > today:
            raise serializers.ValidationError(
                {'last_valuation_date': 'Last valuation date cannot be in the future.'}
            )
        return attrs
