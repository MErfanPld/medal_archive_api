from rest_framework import serializers

from .models import RingPurchaseRecord, RingValuationRecord


class RingPurchaseRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RingPurchaseRecord
        fields = [
            'id', 'purchase_date', 'location', 'seller', 'price', 'currency',
            'notes', 'created_at', 'created_by',
        ]
        read_only_fields = ['id', 'created_at', 'created_by']

    def validate_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('قیمت نمی‌تواند منفی باشد.')
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['item'] = self.context['item']
        if request is not None and getattr(request, 'user', None) is not None and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class RingValuationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RingValuationRecord
        fields = [
            'id', 'value', 'currency', 'valuation_date', 'source', 'notes',
            'created_at', 'created_by',
        ]
        read_only_fields = ['id', 'created_at', 'created_by']

    def validate_value(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('ارزش نمی‌تواند منفی باشد.')
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['item'] = self.context['item']
        if request is not None and getattr(request, 'user', None) is not None and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)
