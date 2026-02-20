from django.db import models
from frames.models import (
    Baguette, Glass, Backing, Hardware, Podramnik, Package,
    Molding, Trosik, Podveski, Material, Passepartout, Work
)
import json


class Order(models.Model):
    """Модель заказа на раму"""
    
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В работе'),
        ('ready', 'Готов'),
        ('issued', 'Выдан'),
    ]
    
    # Размеры картины
    x1 = models.DecimalField('Размер X1 (см)', max_digits=6, decimal_places=2)
    x2 = models.DecimalField('Размер X2 (см)', max_digits=6, decimal_places=2)
    
    # Паспарту (опционально)
    passepartout = models.ForeignKey(
        Passepartout,
        on_delete=models.PROTECT,
        verbose_name='Паспарту',
        related_name='orders',
        blank=True,
        null=True
    )
    passepartout_length = models.DecimalField(
        'Длина паспарту (см)',
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True
    )
    passepartout_width = models.DecimalField(
        'Ширина паспарту (см)',
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    # Основные компоненты (обязательные)
    baguette = models.ForeignKey(
        Baguette,
        on_delete=models.PROTECT,
        verbose_name='Багет',
        related_name='orders'
    )
    
    glass = models.ForeignKey(
        Glass,
        on_delete=models.PROTECT,
        verbose_name='Стекло',
        related_name='orders'
    )
    
    backing = models.ForeignKey(
        Backing,
        on_delete=models.PROTECT,
        verbose_name='Подкладка',
        related_name='orders'
    )
    
    hardware = models.ForeignKey(
        Hardware,
        on_delete=models.PROTECT,
        verbose_name='Фурнитура',
        related_name='orders',
        blank=True,
        null=True
    )
    hardware_quantity = models.PositiveIntegerField('Количество фурнитуры', default=1, blank=True, null=True)
    
    podramnik = models.ForeignKey(
        Podramnik,
        on_delete=models.PROTECT,
        verbose_name='Подрамник',
        related_name='orders',
        blank=True,
        null=True
    )
    
    package = models.ForeignKey(
        Package,
        on_delete=models.PROTECT,
        verbose_name='Упаковка',
        related_name='orders',
        blank=True,
        null=True
    )
    
    work = models.ForeignKey(
        Work,
        on_delete=models.PROTECT,
        verbose_name='Работа',
        related_name='orders',
        blank=True,
        null=True
    )
    
    # Дополнительные компоненты (опциональные)
    molding = models.ForeignKey(
        Molding,
        on_delete=models.PROTECT,
        verbose_name='Молдинг',
        related_name='orders',
        blank=True,
        null=True
    )
    molding_consumption = models.DecimalField(
        'Расход молдинга (м)',
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    trosik = models.ForeignKey(
        Trosik,
        on_delete=models.PROTECT,
        verbose_name='Тросик',
        related_name='orders',
        blank=True,
        null=True
    )
    trosik_length = models.DecimalField(
        'Длина тросика (м)',
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    podveski = models.ForeignKey(
        Podveski,
        on_delete=models.PROTECT,
        verbose_name='Подвески',
        related_name='orders',
        blank=True,
        null=True
    )
    podveski_quantity = models.PositiveIntegerField(
        'Количество подвесок',
        blank=True,
        null=True
    )
    
    # Массив всех рамок (JSON в TextField для совместимости)
    frames_data = models.TextField('Данные всех рамок', blank=True, null=True)
    
    # Информация о клиенте
    customer_name = models.CharField('Имя клиента', max_length=200, blank=True, null=True)
    customer_phone = models.CharField('Телефон клиента', max_length=20, blank=True, null=True)
    payment_method = models.CharField('Способ оплаты', max_length=50, blank=True, null=True, default='наличные')
    comment = models.TextField('Комментарий к заказу', blank=True, null=True)
    
    # Итоговая информация
    total_price = models.DecimalField('Итоговая цена (руб)', max_digits=12, decimal_places=2)
    advance_payment = models.DecimalField('Аванс (руб)', max_digits=12, decimal_places=2, default=0)
    debt = models.DecimalField('Долг (руб)', max_digits=12, decimal_places=2, default=0)
    fulfillment_date = models.DateField('Дата исполнения заказа', blank=True, null=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ #{self.pk} от {self.created_at.strftime('%d.%m.%Y')} ({self.get_status_display()})"
    
    def get_baguette_quantity(self):
        """Расчет количества багета: (X1 + X2) * 2 + 8 * W"""
        return (self.x1 + self.x2) * 2 + 8 * self.baguette.width
    
    def get_glass_area(self):
        """Расчет площади стекла: X1 * X2 (в кв.м)"""
        return (self.x1 * self.x2) / 10000  # Переводим из см² в м²
