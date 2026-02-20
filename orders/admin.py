from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'x1', 'x2', 'baguette', 'status', 
        'total_price', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['id']
    readonly_fields = ['created_at', 'updated_at', 'get_baguette_quantity', 'get_glass_area']
    
    fieldsets = (
        ('Размеры картины', {
            'fields': ('x1', 'x2')
        }),
        ('Паспарту (опционально)', {
            'fields': ('passepartout', 'passepartout_length', 'passepartout_width'),
            'classes': ('collapse',)
        }),
        ('Основные компоненты', {
            'fields': (
                'baguette', 
                'glass', 
                'backing', 
                'hardware', 'hardware_quantity',
                'podramnik', 
                'package'
            )
        }),
        ('Дополнительные компоненты (опционально)', {
            'fields': (
                'molding', 'molding_consumption',
                'trosik', 'trosik_length',
                'podveski', 'podveski_quantity'
            ),
            'classes': ('collapse',)
        }),
        ('Данные клиента', {
            'fields': ('customer_name', 'customer_phone', 'payment_method', 'advance_payment', 'comment'),
            'classes': ('collapse',)
        }),
        ('Итоговая информация', {
            'fields': ('total_price', 'status')
        }),
        ('Расчеты', {
            'fields': ('get_baguette_quantity', 'get_glass_area'),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_baguette_quantity(self, obj):
        """Отображение расчета количества багета"""
        if obj.pk:
            return f"{obj.get_baguette_quantity():.2f} м"
        return "-"
    get_baguette_quantity.short_description = 'Количество багета'
    
    def get_glass_area(self, obj):
        """Отображение площади стекла"""
        if obj.pk:
            return f"{obj.get_glass_area():.4f} кв.м"
        return "-"
    get_glass_area.short_description = 'Площадь стекла'
