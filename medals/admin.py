from django.contrib import admin

from .models import Medal


@admin.register(Medal)
class MedalAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'country', 'year', 'category', 'quality',
        'authenticity', 'catalog_number', 'created_at',
    )
    list_filter = ('quality', 'authenticity', 'country', 'category', 'year')
    search_fields = (
        'name', 'country', 'occasion', 'maker', 'catalog_number',
        'mint_or_manufacturer', 'notes',
    )
    autocomplete_fields = ('category',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Main information', {
            'fields': (
                'name', 'country', 'year', 'occasion', 'historical_period',
                'maker', 'mint_or_manufacturer', 'category',
            ),
        }),
        ('Physical specifications', {
            'fields': (
                'material', 'weight', 'diameter', 'thickness',
                'shape', 'color', 'edge',
            ),
        }),
        ('Condition', {
            'fields': (
                'quality', 'preservation_condition', 'authenticity', 'catalog_number',
            ),
        }),
        ('Purchase', {
            'fields': (
                'purchase_date', 'purchase_location', 'seller',
                'purchase_price', 'purchase_currency',
            ),
        }),
        ('Current value', {
            'fields': ('current_value', 'last_valuation_date'),
        }),
        ('Storage', {
            'fields': ('cabinet_number', 'drawer_number', 'box_number'),
        }),
        ('Notes', {'fields': ('notes',)}),
        ('System', {'fields': ('created_at', 'updated_at')}),
    )
