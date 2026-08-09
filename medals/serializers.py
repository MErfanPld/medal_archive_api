from datetime import date

from django.conf import settings
from rest_framework import serializers

from categories.serializers import CategorySerializer

from .models import (
    Medal,
    MedalImage,
    MedalFile,
    MedalPurchaseRecord,
    MedalValuationRecord,
)
from .validators import validate_medal_image, validate_medal_file


class MedalImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = MedalImage
        fields = [
            'id', 'image', 'image_url', 'image_type', 'caption', 'ordering',
            'is_primary', 'original_filename', 'file_size',
            'uploaded_by', 'uploaded_at',
        ]
        read_only_fields = [
            'id', 'image_url', 'original_filename', 'file_size',
            'uploaded_by', 'uploaded_at',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            url = obj.image.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None

    def validate_image(self, value):
        validate_medal_image(value)
        return value

    def validate(self, attrs):
        medal = self.context.get('medal')
        if medal is None and self.instance is not None:
            medal = self.instance.medal
        if medal is not None and self.instance is None:
            max_count = getattr(settings, 'MEDAL_IMAGE_MAX_COUNT', 10)
            if medal.images.count() >= max_count:
                raise serializers.ValidationError(
                    {'image': f'Maximum of {max_count} images per medal allowed.'}
                )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        medal = self.context['medal']
        uploaded = validated_data.get('image')
        if uploaded is not None:
            validated_data.setdefault(
                'original_filename', getattr(uploaded, 'name', '') or ''
            )
            validated_data.setdefault('file_size', getattr(uploaded, 'size', None))
        if request is not None and getattr(request, 'user', None) is not None:
            if request.user.is_authenticated:
                validated_data['uploaded_by'] = request.user
        validated_data['medal'] = medal
        instance = super().create(validated_data)
        if instance.is_primary:
            medal.images.exclude(pk=instance.pk).update(is_primary=False)
        return instance

    def update(self, instance, validated_data):
        uploaded = validated_data.get('image')
        if uploaded is not None:
            validated_data['original_filename'] = getattr(uploaded, 'name', '') or ''
            validated_data['file_size'] = getattr(uploaded, 'size', None)
        instance = super().update(instance, validated_data)
        if instance.is_primary:
            instance.medal.images.exclude(pk=instance.pk).update(is_primary=False)
        return instance


class MedalFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = MedalFile
        fields = [
            'id', 'file', 'file_url', 'file_type', 'original_filename',
            'content_type', 'file_size', 'notes', 'uploaded_by', 'uploaded_at',
        ]
        read_only_fields = [
            'id', 'file_url', 'original_filename', 'content_type', 'file_size',
            'uploaded_by', 'uploaded_at',
        ]

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            url = obj.file.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None

    def validate_file(self, value):
        validate_medal_file(value)
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        medal = self.context['medal']
        uploaded = validated_data.get('file')
        if uploaded is not None:
            validated_data.setdefault(
                'original_filename', getattr(uploaded, 'name', '') or ''
            )
            validated_data.setdefault('file_size', getattr(uploaded, 'size', None))
            validated_data.setdefault(
                'content_type', getattr(uploaded, 'content_type', '') or ''
            )
        if request is not None and getattr(request, 'user', None) is not None:
            if request.user.is_authenticated:
                validated_data['uploaded_by'] = request.user
        validated_data['medal'] = medal
        return super().create(validated_data)


class MedalPurchaseRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedalPurchaseRecord
        fields = [
            'id', 'purchase_date', 'location', 'seller', 'price', 'currency',
            'notes', 'created_at', 'created_by',
        ]
        read_only_fields = ['id', 'created_at', 'created_by']

    def validate_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Price cannot be negative.')
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['medal'] = self.context['medal']
        if request is not None and getattr(request, 'user', None) is not None:
            if request.user.is_authenticated:
                validated_data['created_by'] = request.user
        return super().create(validated_data)


class MedalValuationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedalValuationRecord
        fields = [
            'id', 'value', 'currency', 'valuation_date', 'source', 'notes',
            'created_at', 'created_by',
        ]
        read_only_fields = ['id', 'created_at', 'created_by']

    def validate_value(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Value cannot be negative.')
        return value

    def validate_valuation_date(self, value):
        if value and value > date.today():
            raise serializers.ValidationError('Valuation date cannot be in the future.')
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['medal'] = self.context['medal']
        if request is not None and getattr(request, 'user', None) is not None:
            if request.user.is_authenticated:
                validated_data['created_by'] = request.user
        instance = super().create(validated_data)
        medal = instance.medal
        medal.current_value = instance.value
        medal.last_valuation_date = instance.valuation_date
        medal.save(update_fields=['current_value', 'last_valuation_date', 'updated_at'])
        return instance


class MedalSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)
    primary_image = serializers.SerializerMethodField()
    images_count = serializers.SerializerMethodField()

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
            'notes', 'primary_image', 'images_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'category_detail',
            'primary_image', 'images_count',
        ]

    def get_images_count(self, obj):
        cache = getattr(obj, '_prefetched_objects_cache', {})
        if 'images' in cache:
            return len(obj.images.all())
        return obj.images.count()

    def get_primary_image(self, obj):
        cache = getattr(obj, '_prefetched_objects_cache', {})
        if 'images' in cache:
            images = list(obj.images.all())
            primary = next((i for i in images if i.is_primary), images[0] if images else None)
        else:
            primary = (
                obj.images.filter(is_primary=True).first()
                or obj.images.order_by('ordering', 'id').first()
            )
        if primary is None:
            return None
        return MedalImageSerializer(primary, context=self.context).data

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
            raise serializers.ValidationError(
                f'Year must be between 1 and {current + 1}.'
            )
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
        purchase_date = attrs.get(
            'purchase_date', getattr(self.instance, 'purchase_date', None)
        )
        last_valuation_date = attrs.get(
            'last_valuation_date', getattr(self.instance, 'last_valuation_date', None)
        )
        today = date.today()
        if purchase_date and purchase_date > today:
            raise serializers.ValidationError(
                {'purchase_date': 'Purchase date cannot be in the future.'}
            )
        if last_valuation_date and last_valuation_date > today:
            raise serializers.ValidationError(
                {'last_valuation_date': 'Last valuation date cannot be in the future.'}
            )
        return attrs


class MuseumMedalSerializer(serializers.ModelSerializer):
    """Rich read-only payload for museum / public detail experience."""

    category_detail = CategorySerializer(source='category', read_only=True)
    images = MedalImageSerializer(many=True, read_only=True)
    files = MedalFileSerializer(many=True, read_only=True)
    purchase_records = MedalPurchaseRecordSerializer(many=True, read_only=True)
    valuation_records = MedalValuationRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Medal
        fields = [
            'id', 'name', 'country', 'year', 'occasion', 'historical_period',
            'maker', 'mint_or_manufacturer', 'category', 'category_detail',
            'material', 'weight', 'diameter', 'thickness', 'shape', 'color', 'edge',
            'quality', 'preservation_condition', 'authenticity', 'catalog_number',
            'current_value', 'last_valuation_date',
            'purchase_date', 'purchase_location', 'seller',
            'purchase_price', 'purchase_currency',
            'cabinet_number', 'drawer_number', 'box_number',
            'notes',
            'images', 'files', 'purchase_records', 'valuation_records',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields
