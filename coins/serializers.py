from django.conf import settings
from rest_framework import serializers

from categories.models import Category
from categories.serializers import CategorySerializer

from .models import Coin, CoinImage
from .validators import validate_coin_image


class CoinImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CoinImage
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
        validate_coin_image(value)
        return value

    def validate(self, attrs):
        coin = self.context.get('coin')
        if coin is None and self.instance is not None:
            coin = self.instance.coin
        if coin is not None and self.instance is None:
            max_count = getattr(settings, 'COIN_IMAGE_MAX_COUNT', 10)
            if coin.images.count() >= max_count:
                raise serializers.ValidationError(
                    {'image': f'حداکثر {max_count} تصویر برای هر قلم مجاز است.'}
                )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        coin = self.context['coin']
        uploaded = validated_data.get('image')
        if uploaded is not None:
            validated_data.setdefault(
                'original_filename', getattr(uploaded, 'name', '') or ''
            )
            validated_data.setdefault('file_size', getattr(uploaded, 'size', None))
        if request is not None and getattr(request, 'user', None) is not None:
            if request.user.is_authenticated:
                validated_data['uploaded_by'] = request.user
        validated_data['coin'] = coin
        instance = super().create(validated_data)
        if instance.is_primary:
            coin.images.exclude(pk=instance.pk).update(is_primary=False)
        return instance

    def update(self, instance, validated_data):
        uploaded = validated_data.get('image')
        if uploaded is not None:
            validated_data['original_filename'] = getattr(uploaded, 'name', '') or ''
            validated_data['file_size'] = getattr(uploaded, 'size', None)
        instance = super().update(instance, validated_data)
        if instance.is_primary:
            instance.coin.images.exclude(pk=instance.pk).update(is_primary=False)
        return instance


class CoinSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        allow_null=True,
        required=False,
        help_text='شناسه دسته‌بندی',
    )
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)
    quality_display = serializers.CharField(source='get_quality_display', read_only=True)
    authenticity_display = serializers.CharField(source='get_authenticity_display', read_only=True)
    primary_image = serializers.SerializerMethodField()
    images_count = serializers.SerializerMethodField()

    class Meta:
        model = Coin
        fields = [
            'id',
            'name',
            'item_type',
            'item_type_display',
            'category_id',
            'category_detail',
            'country',
            'year',
            'year_hijri',
            'historical_period',
            'reign_or_ruler',
            'face_value',
            'denomination',
            'currency_name',
            'material',
            'purity',
            'weight',
            'diameter',
            'thickness',
            'shape',
            'edge',
            'color',
            'serial_number',
            'series',
            'signature',
            'printer',
            'mint',
            'maker',
            'mintage',
            'catalog_number',
            'quality',
            'quality_display',
            'preservation_condition',
            'authenticity',
            'authenticity_display',
            'is_proof',
            'is_commemorative',
            'purchase_date',
            'purchase_location',
            'seller',
            'purchase_price',
            'purchase_currency',
            'current_value',
            'last_valuation_date',
            'cabinet_number',
            'drawer_number',
            'box_number',
            'notes',
            'is_active',
            'primary_image',
            'images_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'primary_image', 'images_count']

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if img is None:
            return None
        return CoinImageSerializer(img, context=self.context).data

    def get_images_count(self, obj):
        return obj.images.count()


class CoinListSerializer(serializers.ModelSerializer):
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    primary_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Coin
        fields = [
            'id',
            'name',
            'item_type',
            'item_type_display',
            'category_name',
            'country',
            'year',
            'face_value',
            'denomination',
            'material',
            'catalog_number',
            'quality',
            'authenticity',
            'current_value',
            'is_active',
            'primary_image_url',
            'created_at',
        ]

    def get_primary_image_url(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if img is None or not img.image:
            return None
        request = self.context.get('request')
        url = img.image.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url
