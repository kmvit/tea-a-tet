from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

from .models import (
    Baguette, Glass, Backing, Hardware, Podramnik, Package,
    Molding, Trosik, Podveski, Material, Passepartout, Stretch,
    Foamboard, TechOperation
)


# Колонки выгрузки багетов: (заголовок, имя поля)
BAGUETTE_EXPORT_COLUMNS = [
    ('ID', 'id'),
    ('Название', 'name'),
    ('Штрихкод', 'barcode'),
    ('Ширина (м)', 'width'),
    ('Цена за метр (руб)', 'price'),
    ('Остаток на складе (м)', 'stock_quantity'),
    ('Дата создания', 'created_at'),
]


@admin.register(Baguette)
class BaguetteAdmin(admin.ModelAdmin):
    list_display = ['name', 'width', 'price', 'stock_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'barcode']
    readonly_fields = ['created_at']
    actions = ['export_to_excel']

    @admin.action(description='Выгрузить в Excel')
    def export_to_excel(self, request, queryset):
        """Выгружает выбранные багеты в файл .xlsx со всеми полями."""
        wb = Workbook()
        ws = wb.active
        ws.title = 'Багеты'

        headers = [title for title, _ in BAGUETTE_EXPORT_COLUMNS]
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)
        ws.freeze_panes = 'A2'

        for baguette in queryset.order_by('name'):
            row = []
            for _, field in BAGUETTE_EXPORT_COLUMNS:
                value = getattr(baguette, field)
                if field == 'created_at' and value:
                    value = timezone.localtime(value).strftime('%d.%m.%Y %H:%M')
                elif field in ('width', 'price', 'stock_quantity'):
                    value = float(value)
                row.append(value if value is not None else '')
            ws.append(row)

        # Ширина колонок по самому длинному значению
        for i, (title, _) in enumerate(BAGUETTE_EXPORT_COLUMNS, start=1):
            longest = max(
                [len(str(title))] + [len(str(r[i - 1].value or '')) for r in ws.iter_rows(min_row=2)]
            )
            ws.column_dimensions[get_column_letter(i)].width = min(longest + 2, 50)

        filename = f"baguettes_{timezone.localtime().strftime('%Y-%m-%d')}.xlsx"
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response
    
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
    list_display = ['name', 'price', 'no_master_work', 'stock_quantity', 'created_at']
    list_editable = ['no_master_work']
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
    list_display = ['name', 'price_per_meter', 'created_at']
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
