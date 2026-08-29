from django.contrib import admin

from .models import Knife, KnifeImage, KnifePurchaseRecord, KnifeValuationRecord


class ImageInline(admin.TabularInline):
    model = KnifeImage
    extra = 0
    readonly_fields = ('uploaded_at', 'file_size', 'original_filename')


class PurchaseInline(admin.TabularInline):
    model = KnifePurchaseRecord
    extra = 0
    readonly_fields = ('created_at',)


class ValuationInline(admin.TabularInline):
    model = KnifeValuationRecord
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Knife)
class KnifeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country', 'year', 'catalog_number', 'authenticity', 'is_active')
    list_filter = ('authenticity', 'condition', 'is_active', 'country')
    search_fields = ('name', 'catalog_number', 'country')
    autocomplete_fields = ('category',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ImageInline, PurchaseInline, ValuationInline]


@admin.register(KnifeImage)
class KnifeImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'image_type', 'is_primary', 'ordering', 'uploaded_at')
    list_filter = ('image_type', 'is_primary')


@admin.register(KnifePurchaseRecord)
class KnifePurchaseRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'purchase_date', 'seller', 'price', 'currency')


@admin.register(KnifeValuationRecord)
class KnifeValuationRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'valuation_date', 'value', 'currency', 'source')
