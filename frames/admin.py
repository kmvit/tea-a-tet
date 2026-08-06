from django.contrib import admin
from .models import (
    Baguette, Glass, Backing, Hardware, Podramnik, Package,
    Molding, Trosik, Podveski, Material, Passepartout, Stretch,
    Foamboard, TechOperation
)


@admin.register(Baguette)
class BaguetteAdmin(admin.ModelAdmin):
    list_display = ['name', 'width', 'price', 'stock_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'width', 'price', 'stock_quantity', 'image')
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Glass)
class GlassAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_sqm', 'stock_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Backing)
class BackingAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Hardware)
class HardwareAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_unit', 'stock_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Podramnik)
class PodramnikAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Molding)
class MoldingAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_meter', 'stock_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Trosik)
class TrosikAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_meter', 'stock_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Podveski)
class PodveskiAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_unit', 'stock_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Passepartout)
class PassepartoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock_quantity', 'image', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Stretch)
class StretchAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_sqm', 'stock_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Foamboard)
class FoamboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock_quantity', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(TechOperation)
class TechOperationAdmin(admin.ModelAdmin):
    list_display = ['operation_type', 'name', 'size_from', 'size_to', 'rate', 'code']
    list_filter = ['operation_type']
    list_editable = ['rate']
    search_fields = ['name', 'code']
    ordering = ['operation_type', 'size_from']
    readonly_fields = ['created_at']
