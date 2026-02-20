from django.contrib import admin
from .models import (
    Baguette, Glass, Backing, Hardware, Podramnik, Package,
    Molding, Trosik, Podveski, Material, Passepartout, Stretch, Work, WorkPriceSettings
)


@admin.register(Baguette)
class BaguetteAdmin(admin.ModelAdmin):
    list_display = ['name', 'width', 'price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'width', 'price', 'image')
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Glass)
class GlassAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_sqm', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Backing)
class BackingAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Hardware)
class HardwareAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_unit', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Podramnik)
class PodramnikAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Molding)
class MoldingAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_meter', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Trosik)
class TrosikAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_meter', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Podveski)
class PodveskiAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_unit', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Passepartout)
class PassepartoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Stretch)
class StretchAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_sqm', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'material_type', 'created_at']
    list_filter = ['material_type', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'price', 'material_type')
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkPriceSettings)
class WorkPriceSettingsAdmin(admin.ModelAdmin):
    list_display = ['max_size_x1', 'max_size_x2', 'multiplier_for_large', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Пороговые размеры для малых рам', {
            'fields': ('max_size_x1', 'max_size_x2'),
            'description': 'Рама считается малой, если обе стороны не превышают эти значения (в любом порядке)'
        }),
        ('Коэффициенты цен', {
            'fields': ('multiplier_for_large',),
            'description': 'Коэффициент умножения стоимости работ для рам больше порогового размера'
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Запретить создание новых записей (только одна запись настроек)"""
        return not WorkPriceSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Запретить удаление настроек"""
        return False
