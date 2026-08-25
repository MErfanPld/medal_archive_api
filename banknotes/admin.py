from django.contrib import admin

from .models import Banknote, BanknoteImage, BanknotePurchaseRecord, BanknoteValuationRecord


class ImageInline(admin.TabularInline):
    model = BanknoteImage
    extra = 0
    readonly_fields = ('uploaded_at', 'file_size', 'original_filename')


class PurchaseInline(admin.TabularInline):
    model = BanknotePurchaseRecord
    extra = 0
    readonly_fields = ('created_at',)


class ValuationInline(admin.TabularInline):
    model = BanknoteValuationRecord
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Banknote)
class BanknoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country', 'year', 'catalog_number', 'authenticity', 'is_active')
    list_filter = ('authenticity', 'condition', 'is_active', 'country')
    search_fields = ('name', 'catalog_number', 'country')
    autocomplete_fields = ('category',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ImageInline, PurchaseInline, ValuationInline]


@admin.register(BanknoteImage)
class BanknoteImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'image_type', 'is_primary', 'ordering', 'uploaded_at')
    list_filter = ('image_type', 'is_primary')


@admin.register(BanknotePurchaseRecord)
class BanknotePurchaseRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'purchase_date', 'seller', 'price', 'currency')


@admin.register(BanknoteValuationRecord)
class BanknoteValuationRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'valuation_date', 'value', 'currency', 'source')
