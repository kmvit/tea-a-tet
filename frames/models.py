from django.db import models


class Baguette(models.Model):
    """Модель багета"""
    name = models.CharField('Название', max_length=200)
    barcode = models.CharField('Штрихкод', max_length=100, blank=True, null=True)
    width = models.DecimalField('Ширина (м)', max_digits=6, decimal_places=2)
    price = models.DecimalField('Цена за метр (руб)', max_digits=10, decimal_places=2)
    image = models.ImageField('Фото', upload_to='baguettes/', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Багет'
        verbose_name_plural = 'Багеты'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} (ширина: {self.width} м, цена: {self.price} руб/м)"


class Glass(models.Model):
    """Модель стекла"""
    name = models.CharField('Название', max_length=200)
    price_per_sqm = models.DecimalField('Цена за кв.м (руб)', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Стекло'
        verbose_name_plural = 'Стекла'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.price_per_sqm} руб/кв.м)"


class Backing(models.Model):
    """Модель подкладки"""
    name = models.CharField('Название', max_length=200)
    price = models.DecimalField('Цена (руб)', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Подкладка'
        verbose_name_plural = 'Подкладки'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.price} руб)"


class Hardware(models.Model):
    """Модель фурнитуры"""
    name = models.CharField('Название', max_length=200)
    price_per_unit = models.DecimalField('Цена за штуку (руб)', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Фурнитура'
        verbose_name_plural = 'Фурнитура'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.price_per_unit} руб/шт)"


class Podramnik(models.Model):
    """Модель подрамника"""
    name = models.CharField('Название', max_length=200)
    price = models.DecimalField('Цена (руб)', max_digits=10, decimal_places=2)
    consumption = models.DecimalField('Расход (м)', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Подрамник'
        verbose_name_plural = 'Подрамники'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.price} руб, расход: {self.consumption} м)"


class Passepartout(models.Model):
    """Модель паспарту"""
    name = models.CharField('Название', max_length=200)
    price = models.DecimalField('Цена (руб)', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Паспарту'
        verbose_name_plural = 'Паспарту'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.price} руб)"


class Material(models.Model):
    """Модель материалов"""
    name = models.CharField('Название', max_length=200)
    price = models.DecimalField('Цена (руб)', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.price} руб)"


class Package(models.Model):
    """Модель упаковки"""
    name = models.CharField('Название', max_length=200)
    price = models.DecimalField('Цена (руб)', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Упаковка'
        verbose_name_plural = 'Упаковки'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.price} руб)"


class Molding(models.Model):
    """Модель молдинга"""
    name = models.CharField('Название', max_length=200)
    price_per_meter = models.DecimalField('Цена за метр (руб)', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Молдинг'
        verbose_name_plural = 'Молдинги'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.price_per_meter} руб/м)"


class Trosik(models.Model):
    """Модель тросика"""
    name = models.CharField('Название', max_length=200)
    price_per_meter = models.DecimalField('Цена за метр (руб)', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Тросик'
        verbose_name_plural = 'Тросики'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.price_per_meter} руб/м)"


class Podveski(models.Model):
    """Модель подвесок"""
    name = models.CharField('Название', max_length=200)
    price_per_unit = models.DecimalField('Цена за штуку (руб)', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Подвески'
        verbose_name_plural = 'Подвески'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.price_per_unit} руб/шт)"


class Stretch(models.Model):
    """Модель натяжки"""
    name = models.CharField('Название', max_length=200)
    price_per_sqm = models.DecimalField('Цена за кв.м (руб)', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Натяжка'
        verbose_name_plural = 'Натяжки'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.price_per_sqm} руб/кв.м)"


class Work(models.Model):
    """Модель работы"""
    MATERIAL_TYPE_CHOICES = [
        ('', 'Не привязана к материалу'),
        ('baguette', 'Багет'),
        ('podramnik', 'Подрамник'),
        ('glass', 'Стекло'),
        ('passepartout', 'Паспарту'),
        ('stretch', 'Натяжка'),
        ('backing', 'Подкладка'),
        ('hardware', 'Фурнитура'),
        ('molding', 'Молдинг'),
        ('trosik', 'Тросик'),
        ('podveski', 'Подвески'),
    ]
    
    name = models.CharField('Название', max_length=200)
    price = models.DecimalField('Цена (руб)', max_digits=10, decimal_places=2)
    material_type = models.CharField(
        'Тип материала',
        max_length=50,
        choices=MATERIAL_TYPE_CHOICES,
        blank=True,
        default='',
        help_text='Тип материала, при выборе которого автоматически добавляется эта работа'
    )
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Работа'
        verbose_name_plural = 'Работы'
        ordering = ['name']
    
    def __str__(self):
        material_info = ""
        if self.material_type:
            material_info = f" [{self.get_material_type_display()}]"
        return f"{self.name} ({self.price} руб){material_info}"


class WorkPriceSettings(models.Model):
    """Настройки расчета стоимости работ в зависимости от размера рамы"""
    max_size_x1 = models.DecimalField(
        'Максимальный размер первой стороны (см)',
        max_digits=6,
        decimal_places=2,
        default=60,
        help_text='Максимальный размер первой стороны для малых рам'
    )
    max_size_x2 = models.DecimalField(
        'Максимальный размер второй стороны (см)',
        max_digits=6,
        decimal_places=2,
        default=50,
        help_text='Максимальный размер второй стороны для малых рам'
    )
    multiplier_for_large = models.DecimalField(
        'Коэффициент для больших рам',
        max_digits=4,
        decimal_places=2,
        default=1.5,
        help_text='Коэффициент умножения стоимости работ для рам больше порогового размера'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Настройки стоимости работ'
        verbose_name_plural = 'Настройки стоимости работ'
    
    def __str__(self):
        return f"Настройки: малые рамы до {self.max_size_x1}x{self.max_size_x2}, коэффициент {self.multiplier_for_large}"
    
    @classmethod
    def get_settings(cls):
        """Получить настройки (Singleton pattern)"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    def save(self, *args, **kwargs):
        """Ограничение: только одна запись настроек"""
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Запретить удаление настроек"""
        pass
