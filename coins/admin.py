from django.contrib import admin

from .models import Coin, CoinImage


class CoinImageInline(admin.TabularInline):
    model = CoinImage
    extra = 0
    readonly_fields = ('uploaded_at', 'file_size', 'original_filename')


@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'item_type', 'country', 'year',
        'face_value', 'denomination', 'quality', 'authenticity', 'is_active',
    )
    list_filter = ('item_type', 'authenticity', 'quality', 'is_active', 'country')
    search_fields = ('name', 'catalog_number', 'serial_number', 'country', 'mint')
    autocomplete_fields = ('category',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CoinImageInline]


@admin.register(CoinImage)
class CoinImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'coin', 'image_type', 'is_primary', 'ordering', 'uploaded_at')
    list_filter = ('image_type', 'is_primary')
    search_fields = ('coin__name', 'caption', 'original_filename')
