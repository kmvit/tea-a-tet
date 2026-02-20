from django.core.management.base import BaseCommand
from decimal import Decimal
from frames.models import (
    Hardware, Podveski, Glass, Backing, Trosik, Podramnik, Package, Molding, Material
)


class Command(BaseCommand):
    help = 'Добавление тестовых данных в справочники'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начинаю добавление тестовых данных...\n'))
        
        # Фурнитура
        self.stdout.write('Добавляю фурнитуру...')
        hardware_data = [
            ('ЗАЖИМ БОЛЬ', 3),
            ('ЗАЖИМ МАЛЫЙ', 8),
            ('НОЖКА ПОДКЛАДА', 7),
            ('НОЖКА PAMA', 9),
            ('ПЕТЛЯ НОЖКА', 12),
            ('пластина уголок', 5),
            ('ПОДСТАВКА БОЛЬ', 6),
            ('ПОДСТАВКА МАДАЯ', 2),
            ('ФОТОУГОЛОК БИЛЬ', 1),
            ('ФОТОУГОЛОК МАЛЬ', 13),
            ('Фурнитура,алюминий (малый)', 14),
            ('Фурнитура,алюминий(боль)', 10),
            ('Шкант мебель 6мм', 11),
            ('Шкант мебель 8 мм', 11),
        ]
        
        for name, price in hardware_data:
            obj, created = Hardware.objects.get_or_create(
                name=name,
                defaults={'price_per_unit': Decimal(str(price))}
            )
            if created:
                self.stdout.write(f'  ✓ Создан: {name} - {price} руб/шт')
            else:
                self.stdout.write(f'  - Уже существует: {name}')
        
        # Подвески
        self.stdout.write('\nДобавляю подвески...')
        podveski_data = [
            ('D-КОЛЬЦО', 1),
            ('FRICTION', 11),
            ('БОЛЬШОЕ D-КОЛЬЦО', 90),
            ('ДЕКОРАТИВНАЯ', 40),
            ('ЗЕРКАЛЬНАЯ БОЛЬШАЯ', 55),
            ('ЗЕРКАЛЬНАЯ МАЛАЯ', 55),
            ('КРОКО ДИЛ-БГ', 8),
            ('КРОКОДИЛ-С', 1),
            ('МАЛОЕ D-КОЛЬЦО', 10),
            ('НАКЛОННЫЕ D-КОЛЬЦА', 10),
        ]
        
        for name, price in podveski_data:
            obj, created = Podveski.objects.get_or_create(
                name=name,
                defaults={'price_per_unit': Decimal(str(price))}
            )
            if created:
                self.stdout.write(f'  ✓ Создан: {name} - {price} руб/шт')
            else:
                self.stdout.write(f'  - Уже существует: {name}')
        
        # Стекло
        self.stdout.write('\nДобавляю стекло...')
        glass_data = [
            ('MATOBOE', 1550),
            ('ПЛЕКС.МАТОВЫЙ', 2300),
            ('ПРОЗРАЧ.ПЛЕКС', 2300),
            ('ПРОСТОЕ', 1550),
        ]
        
        for name, price in glass_data:
            obj, created = Glass.objects.get_or_create(
                name=name,
                defaults={'price_per_sqm': Decimal(str(price))}
            )
            if created:
                self.stdout.write(f'  ✓ Создан: {name} - {price} руб/кв.м')
            else:
                self.stdout.write(f'  - Уже существует: {name}')
        
        # Подкладка
        self.stdout.write('\nДобавляю подкладку...')
        backing_data = [
            ('ДВП 6мм', 900),
            ('ОБЫЧНАЯ', 450),
            ('пенокартон бін 3мм', 900),
            ('пенокартон бін 5мм', 900),
            ('ПЕНОКАРТОН С/К 5мм', 900),
            ('ПЕНОКАРТОН С\\К 3мм', 900),
            ('СЕРАЯ', 900),
            ('фанера перфорированная', 900),
        ]
        
        for name, price in backing_data:
            obj, created = Backing.objects.get_or_create(
                name=name,
                defaults={'price': Decimal(str(price))}
            )
            if created:
                self.stdout.write(f'  ✓ Создан: {name} - {price} руб')
            else:
                self.stdout.write(f'  - Уже существует: {name}')
        
        # Тросик
        self.stdout.write('\nДобавляю тросик...')
        trosik_data = [
            ('Nº 1 ЛАТУНЬ', 90),
            ('Nº 2 ЛАТУНЬ', 100),
            ('Nº 3 ЛАТУНЬ', 110),
            ('СТАЛЬ Nº 1', 90),
            ('СТАЛЬ Nº 2', 100),
        ]
        
        for name, price in trosik_data:
            obj, created = Trosik.objects.get_or_create(
                name=name,
                defaults={'price_per_meter': Decimal(str(price))}
            )
            if created:
                self.stdout.write(f'  ✓ Создан: {name} - {price} руб/м')
            else:
                self.stdout.write(f'  - Уже существует: {name}')
        
        # Материалы
        self.stdout.write('\nДобавляю материалы...')
        materials_data = [
            ('ГОФРАКАРТОН', 100),
            ('ДВП 6мм', 900),
            ('ФАНЕРА 10мм', 1000),
            ('ФОТОБУМАГА', 3000),
            ('ХОЛСТ', 4000),
            ('ЦЕЛОФАН', 100),
        ]
        
        for name, price in materials_data:
            obj, created = Material.objects.get_or_create(
                name=name,
                defaults={'price': Decimal(str(price))}
            )
            if created:
                self.stdout.write(f'  ✓ Создан: {name} - {price} руб')
            else:
                self.stdout.write(f'  - Уже существует: {name}')
        
        # Подрамник
        self.stdout.write('\nДобавляю подрамник...')
        podramnik_data = [
            ('РЕЙКА 40х18 МАЛ', 150),
            ('РЕЙКА 50х18 СРЕД', 275),
            ('РЕЙКА 60х18 Б0Л', 330),
            ('РЕЙКА 60х30 БОЛ,УСИЛЕН', 400),
            ('РЕЙКА ДЛЯ КОРОБКИ 40Х20', 55),
        ]
        
        for name, price in podramnik_data:
            obj, created = Podramnik.objects.get_or_create(
                name=name,
                defaults={'price': Decimal(str(price))}
            )
            if created:
                self.stdout.write(f'  ✓ Создан: {name} - {price} руб')
            else:
                self.stdout.write(f'  - Уже существует: {name}')
        
        # Добавляю базовые данные для Упаковки и Молдинга
        self.stdout.write('\nДобавляю базовые данные...')
        
        # Упаковка
        package_data = [
            ('Стандартная упаковка', 200),
            ('Защитная упаковка', 400),
        ]
        for name, price in package_data:
            obj, created = Package.objects.get_or_create(
                name=name,
                defaults={'price': Decimal(str(price))}
            )
            if created:
                self.stdout.write(f'  ✓ Создан: {name} - {price} руб')
        
        # Молдинг
        molding_data = [
            ('Молдинг стандартный', 150),
            ('Молдинг декоративный', 250),
        ]
        for name, price in molding_data:
            obj, created = Molding.objects.get_or_create(
                name=name,
                defaults={'price_per_meter': Decimal(str(price))}
            )
            if created:
                self.stdout.write(f'  ✓ Создан: {name} - {price} руб/м')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Тестовые данные успешно добавлены!'))
