from django.db import models


class Baguette(models.Model):
    """Модель багета"""
    name = models.CharField('Название', max_length=200)
    barcode = models.CharField('Штрихкод', max_length=100, blank=True, null=True)
    width = models.DecimalField('Ширина (м)', max_digits=6, decimal_places=2)
    price = models.DecimalField('Цена за метр (руб)', max_digits=10, decimal_places=2)
    stock_quantity = models.DecimalField(
        'Количество на складе (м)',
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Фактическое наличие на складе в метрах. Списывается при каждом заказе.'
    )
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
    stock_quantity = models.DecimalField(
        'Количество на складе (кв.м)',
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Фактическое наличие на складе в кв.м. Списывается при каждом заказе.'
    )
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
    stock_quantity = models.DecimalField(
        'Количество на складе (шт)',
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Фактическое наличие на складе в штуках. Списывается при каждом заказе.'
    )
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
    stock_quantity = models.DecimalField(
        'Количество на складе (шт)',
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Фактическое наличие на складе в штуках. Списывается при каждом заказе.'
    )
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
    stock_quantity = models.DecimalField(
        'Количество на складе (шт)',
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Фактическое наличие на складе в штуках. Списывается при каждом заказе.'
    )
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
    stock_quantity = models.DecimalField(
        'Количество на складе (шт)',
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Фактическое наличие на складе в штуках (листах). Списывается при каждом заказе.'
    )
    image = models.ImageField('Фото', upload_to='passepartout/', blank=True, null=True)
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
    stock_quantity = models.DecimalField(
        'Количество на складе (шт)',
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Фактическое наличие на складе в штуках. Списывается при каждом заказе.'
    )
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
    stock_quantity = models.DecimalField(
        'Количество на складе (шт)',
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Фактическое наличие на складе в штуках. Списывается при каждом заказе.'
    )
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
    stock_quantity = models.DecimalField(
        'Количество на складе (м)',
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Фактическое наличие на складе в метрах. Списывается при каждом заказе.'
    )
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
    stock_quantity = models.DecimalField(
        'Количество на складе (м)',
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Фактическое наличие на складе в метрах. Списывается при каждом заказе.'
    )
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
    stock_quantity = models.DecimalField(
        'Количество на складе (шт)',
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Фактическое наличие на складе в штуках. Списывается при каждом заказе.'
    )
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
    stock_quantity = models.DecimalField(
        'Количество на складе (кв.м)',
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Фактическое наличие на складе в кв.м. Списывается при каждом заказе.'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Натяжка'
        verbose_name_plural = 'Натяжки'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.price_per_sqm} руб/кв.м)"


class Foamboard(models.Model):
    """Пенокартон (накатка на пенокартон) — материал, аналог подкладки"""
    name = models.CharField('Название', max_length=200)
    price = models.DecimalField('Цена за кв.м (руб)', max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.DecimalField(
        'Количество на складе (кв.м)',
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Фактическое наличие на складе в кв.м. Списывается при каждом заказе.'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Пенокартон'
        verbose_name_plural = 'Пенокартон (накатка)'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.price} руб/кв.м)"


class TechOperation(models.Model):
    """
    Технологическая операция (работа) из 1С.
    Расценка подбирается по диапазону: От <= макс(длина, ширина) <= До.
    Для операций со спец-формулой (натяжка, упаковка, сложности, молдинг)
    диапазон и расценка могут быть пустыми — расценка считается в коде.
    """
    OPERATION_TYPES = [
        ('rama', 'Изготовление рамы'),
        ('rama2', 'Изготовление двойных рам'),
        ('rama3', 'Изготовление тройных рам'),
        ('passepartout', 'Паспарту'),
        ('passepartout2', 'Паспарту второе'),
        ('passepartout3', 'Паспарту третье'),
        ('backing', 'Резка подкладки'),
        ('backing2', 'Резка подкладки2'),
        ('glass', 'Резка стекла'),
        ('glass2', 'Резка стекла2'),
        ('podramnik', 'Подрамник'),
        ('foamboard', 'Накатка на пенокартон'),
        ('stretch', 'Натяжка холста'),
        ('molding', 'Молдинг'),
        ('complexity_frame', 'Сложность рамы'),
        ('complexity_pp', 'Сложность паспарту'),
        ('complexity_mount', 'Крепление объекта'),
        ('package', 'Упаковка'),
    ]

    code = models.IntegerField('Код 1С', null=True, blank=True, db_index=True)
    operation_type = models.CharField('Вид операции', max_length=32, choices=OPERATION_TYPES, db_index=True)
    name = models.CharField('Наименование', max_length=200)
    size_from = models.DecimalField('От (см)', max_digits=7, decimal_places=2, null=True, blank=True)
    size_to = models.DecimalField('До (см)', max_digits=7, decimal_places=2, null=True, blank=True)
    rate = models.DecimalField('Расценка', max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Технологическая операция (работа)'
        verbose_name_plural = 'Технологические операции (работы)'
        ordering = ['operation_type', 'size_from']

    def __str__(self):
        rng = ''
        if self.size_from is not None or self.size_to is not None:
            rng = f" [{self.size_from or 0}–{self.size_to or '∞'}]"
        return f"{self.get_operation_type_display()}{rng}: {self.rate if self.rate is not None else '—'}"

    @classmethod
    def find_by_size(cls, operation_type, size):
        """
        Возвращает подходящую операцию по виду и размеру (макс. стороны в см):
        строка, где От <= size <= До (пустое От = 0, пустое До = ∞).
        """
        from decimal import Decimal
        try:
            size = Decimal(str(size))
        except Exception:
            return None
        for op in cls.objects.filter(operation_type=operation_type):
            lo = op.size_from if op.size_from is not None else Decimal('0')
            hi = op.size_to if op.size_to is not None else Decimal('9999999')
            if lo <= size <= hi:
                return op
        return None

