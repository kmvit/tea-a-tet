import xlrd
from decimal import Decimal
from django.core.management.base import BaseCommand
from frames.models import Baguette


class Command(BaseCommand):
    help = 'Импорт багетов из Excel файла'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='справочник багет.xls',
            help='Путь к Excel файлу с багетами'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        try:
            # Открываем Excel файл
            wb = xlrd.open_workbook(file_path, encoding_override='cp1251')
            ws = wb.sheet_by_index(0)
            
            self.stdout.write(self.style.SUCCESS(f'Открыт файл: {file_path}'))
            self.stdout.write(f'Всего строк: {ws.nrows}')
            
            # Находим строку с заголовками (обычно это строка 5, индекс 5)
            header_row = 5
            
            # Проверяем заголовки
            headers = [ws.cell_value(header_row, col) for col in range(ws.ncols)]
            self.stdout.write(f'Заголовки: {headers}')
            
            # Импортируем данные
            imported_count = 0
            skipped_count = 0
            
            for row_idx in range(header_row + 1, ws.nrows):
                try:
                    # Читаем данные из строки
                    number = ws.cell_value(row_idx, 0)  # Номер
                    name = ws.cell_value(row_idx, 1)    # Наименование
                    width = ws.cell_value(row_idx, 2)   # Ширина
                    price = ws.cell_value(row_idx, 3)   # Цена руб/метр
                    
                    # Пропускаем пустые строки
                    if not name or name == '':
                        continue
                    
                    # Пропускаем строки без цены или ширины
                    if not price or not width:
                        self.stdout.write(
                            self.style.WARNING(f'Пропущена строка {row_idx + 1}: нет цены или ширины')
                        )
                        skipped_count += 1
                        continue
                    
                    # Преобразуем данные
                    try:
                        width_decimal = Decimal(str(width))
                        price_decimal = Decimal(str(price))
                    except (ValueError, TypeError) as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Пропущена строка {row_idx + 1}: ошибка преобразования ({e})'
                            )
                        )
                        skipped_count += 1
                        continue
                    
                    # Создаем или обновляем багет
                    baguette, created = Baguette.objects.update_or_create(
                        name=name.strip(),
                        defaults={
                            'width': width_decimal,
                            'price': price_decimal,
                        }
                    )
                    
                    if created:
                        imported_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Создан: {baguette.name} (ширина: {width_decimal}, цена: {price_decimal})'
                            )
                        )
                    else:
                        self.stdout.write(
                            f'Обновлен: {baguette.name}'
                        )
                        imported_count += 1
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Ошибка в строке {row_idx + 1}: {e}')
                    )
                    skipped_count += 1
                    continue
            
            # Итоги
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Импорт завершен!\n'
                    f'Импортировано: {imported_count}\n'
                    f'Пропущено: {skipped_count}'
                )
            )
        
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл не найден: {file_path}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при импорте: {e}')
            )
