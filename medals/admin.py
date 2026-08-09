from django.contrib import admin
from .models import Medal, MedalImage, MedalFile, MedalPurchaseRecord, MedalValuationRecord


class MedalImageInline(admin.TabularInline):
    model = MedalImage
    extra = 0
    readonly_fields = ('uploaded_at', 'file_size', 'original_filename')


@admin.register(Medal)
class MedalAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country', 'year', 'category', 'quality', 'catalog_number', 'created_at')
    list_filter = ('quality', 'authenticity', 'country', 'category', 'year')
    search_fields = ('name', 'country', 'occasion', 'maker', 'catalog_number', 'notes')
    autocomplete_fields = ('category',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MedalImageInline]


@admin.register(MedalPurchaseRecord)
class MedalPurchaseRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'medal', 'purchase_date', 'seller', 'price', 'currency', 'created_at')
    autocomplete_fields = ('medal',)
    readonly_fields = ('created_at',)


@admin.register(MedalValuationRecord)
class MedalValuationRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'medal', 'value', 'currency', 'valuation_date', 'source', 'created_at')
    autocomplete_fields = ('medal',)
    readonly_fields = ('created_at',)
