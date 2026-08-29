from django.contrib import admin

from .models import Stamp, StampImage, StampPurchaseRecord, StampValuationRecord


class ImageInline(admin.TabularInline):
    model = StampImage
    extra = 0
    readonly_fields = ('uploaded_at', 'file_size', 'original_filename')


class PurchaseInline(admin.TabularInline):
    model = StampPurchaseRecord
    extra = 0
    readonly_fields = ('created_at',)


class ValuationInline(admin.TabularInline):
    model = StampValuationRecord
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Stamp)
class StampAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country', 'year', 'catalog_number', 'authenticity', 'is_active')
    list_filter = ('authenticity', 'condition', 'is_active', 'country')
    search_fields = ('name', 'catalog_number', 'country')
    autocomplete_fields = ('category',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ImageInline, PurchaseInline, ValuationInline]


@admin.register(StampImage)
class StampImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'image_type', 'is_primary', 'ordering', 'uploaded_at')
    list_filter = ('image_type', 'is_primary')


@admin.register(StampPurchaseRecord)
class StampPurchaseRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'purchase_date', 'seller', 'price', 'currency')


@admin.register(StampValuationRecord)
class StampValuationRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'valuation_date', 'value', 'currency', 'source')
