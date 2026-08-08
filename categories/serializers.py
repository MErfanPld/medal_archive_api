from django.utils.text import slugify
from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'slug': {'required': False, 'allow_blank': True}}

    def validate_name(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Name is required.')
        qs = Category.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('A category with this name already exists.')
        return value

    def validate_slug(self, value):
        if value is None or value == '':
            return value
        value = slugify(value)
        if not value:
            raise serializers.ValidationError('Invalid slug.')
        qs = Category.objects.filter(slug=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('A category with this slug already exists.')
        return value

    def create(self, validated_data):
        if not validated_data.get('slug') and validated_data.get('name'):
            validated_data['slug'] = slugify(validated_data['name']) or 'category'
        return super().create(validated_data)
