from django.conf import settings
from rest_framework import serializers

from categories.models import Category
from categories.serializers import CategorySerializer

from .models import Tasbih, TasbihImage
from .validators import validate_tasbih_image


class TasbihImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = TasbihImage
        fields = [
            'id', 'image', 'image_url', 'image_type', 'caption', 'ordering',
            'is_primary', 'original_filename', 'file_size', 'uploaded_by', 'uploaded_at',
        ]
        read_only_fields = [
            'id', 'image_url', 'original_filename', 'file_size', 'uploaded_by', 'uploaded_at',
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
        validate_tasbih_image(value)
        return value

    def validate(self, attrs):
        item = self.context.get('item')
        if item is None and self.instance is not None:
            item = self.instance.item
        if item is not None and self.instance is None:
            max_count = getattr(settings, 'COLLECTION_IMAGE_MAX_COUNT', 10)
            if item.images.count() >= max_count:
                raise serializers.ValidationError({'image': f'حداکثر {max_count} تصویر مجاز است.'})
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        item = self.context['item']
        uploaded = validated_data.get('image')
        if uploaded is not None:
            validated_data.setdefault('original_filename', getattr(uploaded, 'name', '') or '')
            validated_data.setdefault('file_size', getattr(uploaded, 'size', None))
        if request is not None and getattr(request, 'user', None) is not None and request.user.is_authenticated:
            validated_data['uploaded_by'] = request.user
        validated_data['item'] = item
        instance = super().create(validated_data)
        if instance.is_primary:
            item.images.exclude(pk=instance.pk).update(is_primary=False)
        return instance

    def update(self, instance, validated_data):
        uploaded = validated_data.get('image')
        if uploaded is not None:
            validated_data['original_filename'] = getattr(uploaded, 'name', '') or ''
            validated_data['file_size'] = getattr(uploaded, 'size', None)
        instance = super().update(instance, validated_data)
        if instance.is_primary:
            instance.item.images.exclude(pk=instance.pk).update(is_primary=False)
        return instance


class TasbihSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category', queryset=Category.objects.all(), allow_null=True, required=False,
    )
    authenticity_display = serializers.CharField(source='get_authenticity_display', read_only=True)
    primary_image = serializers.SerializerMethodField()
    images_count = serializers.SerializerMethodField()

    class Meta:
        model = Tasbih
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_fields(self):
        fields = super().get_fields()
        # expose category_id write, hide raw category FK if present
        if 'category' in fields and 'category_id' in fields:
            fields['category'].read_only = True
        fields['primary_image'] = serializers.SerializerMethodField()
        fields['images_count'] = serializers.SerializerMethodField()
        fields['category_detail'] = CategorySerializer(source='category', read_only=True)
        fields['authenticity_display'] = serializers.CharField(source='get_authenticity_display', read_only=True)
        return fields

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if img is None:
            return None
        return TasbihImageSerializer(img, context=self.context).data

    def get_images_count(self, obj):
        return obj.images.count()


class TasbihListSerializer(serializers.ModelSerializer):
    primary_image_url = serializers.SerializerMethodField()
    authenticity_display = serializers.CharField(source='get_authenticity_display', read_only=True)

    class Meta:
        model = Tasbih
        fields = ['id', 'name', 'country', 'year', 'catalog_number', 'authenticity', 'authenticity_display', 'current_value', 'is_active', 'primary_image_url', 'created_at']

    def get_primary_image_url(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if img is None or not img.image:
            return None
        request = self.context.get('request')
        url = img.image.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url
