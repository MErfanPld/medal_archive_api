from rest_framework import serializers

from .models import CoinPurchaseRecord, CoinValuationRecord


class CoinPurchaseRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinPurchaseRecord
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
        validated_data['coin'] = self.context['coin']
        if request is not None and getattr(request, 'user', None) is not None:
            if request.user.is_authenticated:
                validated_data['created_by'] = request.user
        return super().create(validated_data)


class CoinValuationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinValuationRecord
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
        validated_data['coin'] = self.context['coin']
        if request is not None and getattr(request, 'user', None) is not None:
            if request.user.is_authenticated:
                validated_data['created_by'] = request.user
        return super().create(validated_data)
