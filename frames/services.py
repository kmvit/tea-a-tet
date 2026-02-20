from decimal import Decimal
from typing import Dict, Optional
from .models import Baguette, Glass, Backing, Hardware, Podramnik, Package, Molding, Trosik, Podveski, Material, Passepartout, Stretch, Work, WorkPriceSettings


class PriceCalculator:
    """Класс для расчета стоимости заказа на раму"""
    
    @staticmethod
    def is_small_frame(x1: Decimal, x2: Decimal) -> bool:
        """
        Определяет, является ли рама малой в соответствии с настройками
        Рама считается малой, если обе стороны не превышают пороговые значения
        (x1 <= max_x1 И x2 <= max_x2) ИЛИ (x1 <= max_x2 И x2 <= max_x1)
        """
        settings = WorkPriceSettings.get_settings()
        return ((x1 <= settings.max_size_x1 and x2 <= settings.max_size_x2) or
                (x1 <= settings.max_size_x2 and x2 <= settings.max_size_x1))
    
    @staticmethod
    def calculate_baguette_quantity(x1: Decimal, x2: Decimal, width: Decimal) -> Decimal:
        """
        Расчет количества багета по формуле: (X1 + X2) * 2 + 8 * W
        где W - ширина багета в см, результат в метрах
        """
        # Переводим см в метры для ширины
        width_meters = width / 100
        # (X1 + X2) в см, переводим в метры
        perimeter = ((x1 + x2) * 2) / 100
        # Добавляем 8 * ширину багета
        total = perimeter + 8 * width_meters
        return total
    
    @staticmethod
    def calculate_glass_area(x1: Decimal, x2: Decimal) -> Decimal:
        """
        Расчет площади стекла: X1 * X2 в кв.м
        """
        # X1 и X2 в см, переводим в метры
        area_sqm = (x1 / 100) * (x2 / 100)
        return area_sqm
    
    @staticmethod
    def calculate_baguette_price(
        x1: Decimal, 
        x2: Decimal, 
        baguette: Baguette
    ) -> Dict[str, Decimal]:
        """Расчет стоимости багета"""
        quantity = PriceCalculator.calculate_baguette_quantity(x1, x2, baguette.width)
        price = quantity * baguette.price
        return {
            'quantity': quantity,
            'unit_price': baguette.price,
            'total_price': price
        }
    
    @staticmethod
    def calculate_glass_price(
        x1: Decimal, 
        x2: Decimal, 
        glass: Glass
    ) -> Dict[str, Decimal]:
        """Расчет стоимости стекла"""
        area = PriceCalculator.calculate_glass_area(x1, x2)
        price = area * glass.price_per_sqm
        return {
            'area': area,
            'unit_price': glass.price_per_sqm,
            'total_price': price
        }
    
    @staticmethod
    def calculate_stretch_price(
        x1: Decimal, 
        x2: Decimal, 
        stretch: Stretch
    ) -> Dict[str, Decimal]:
        """Расчет стоимости натяжки"""
        area = PriceCalculator.calculate_glass_area(x1, x2)
        price = area * stretch.price_per_sqm
        return {
            'area': area,
            'unit_price': stretch.price_per_sqm,
            'total_price': price
        }
    
    @staticmethod
    def calculate_total_price(
        x1: Decimal,
        x2: Decimal,
        baguette_id: Optional[int] = None,
        glass_id: Optional[int] = None,
        backing_id: Optional[int] = None,
        hardware_id: Optional[int] = None,
        hardware_quantity: int = 1,
        podramnik_id: Optional[int] = None,
        package_id: Optional[int] = None,
        molding_id: Optional[int] = None,
        molding_consumption: Optional[Decimal] = None,
        trosik_id: Optional[int] = None,
        trosik_length: Optional[Decimal] = None,
        podveski_id: Optional[int] = None,
        podveski_quantity: Optional[int] = None,
        passepartout_id: Optional[int] = None,
        passepartout_length: Optional[Decimal] = None,
        passepartout_width: Optional[Decimal] = None,
        stretch_id: Optional[int] = None,
        work_id: Optional[int] = None,
    ) -> Dict[str, any]:
        """
        Расчет стоимости заказа (частичный или полный)
        Возвращает детализацию по каждому компоненту и итоговую сумму
        Все поля кроме x1 и x2 опциональны
        """
        
        result = {
            'components': {},
            'total_price': Decimal('0')
        }
        
        # Список выбранных типов материалов для автоматического добавления работ
        selected_material_types = []
        
        try:
            # Багет
            if baguette_id:
                baguette = Baguette.objects.get(pk=baguette_id)
                baguette_calc = PriceCalculator.calculate_baguette_price(x1, x2, baguette)
                result['components']['baguette'] = {
                    'name': baguette.name,
                    'quantity': float(baguette_calc['quantity']),
                    'unit_price': float(baguette_calc['unit_price']),
                    'total_price': float(baguette_calc['total_price'])
                }
                result['total_price'] += baguette_calc['total_price']
                selected_material_types.append('baguette')
            
            # Стекло
            if glass_id:
                glass = Glass.objects.get(pk=glass_id)
                glass_calc = PriceCalculator.calculate_glass_price(x1, x2, glass)
                result['components']['glass'] = {
                    'name': glass.name,
                    'area': float(glass_calc['area']),
                    'unit_price': float(glass_calc['unit_price']),
                    'total_price': float(glass_calc['total_price'])
                }
                result['total_price'] += glass_calc['total_price']
                selected_material_types.append('glass')
            
            # Подкладка
            if backing_id:
                backing = Backing.objects.get(pk=backing_id)
                result['components']['backing'] = {
                    'name': backing.name,
                    'total_price': float(backing.price)
                }
                result['total_price'] += backing.price
                selected_material_types.append('backing')
            
            # Фурнитура
            if hardware_id:
                hardware = Hardware.objects.get(pk=hardware_id)
                hardware_price = hardware.price_per_unit * hardware_quantity
                result['components']['hardware'] = {
                    'name': hardware.name,
                    'quantity': hardware_quantity,
                    'unit_price': float(hardware.price_per_unit),
                    'total_price': float(hardware_price)
                }
                result['total_price'] += hardware_price
                selected_material_types.append('hardware')
            
            # Подрамник
            if podramnik_id:
                podramnik = Podramnik.objects.get(pk=podramnik_id)
                result['components']['podramnik'] = {
                    'name': podramnik.name,
                    'total_price': float(podramnik.price)
                }
                result['total_price'] += podramnik.price
                selected_material_types.append('podramnik')
            
            # Упаковка
            if package_id:
                package = Package.objects.get(pk=package_id)
                result['components']['package'] = {
                    'name': package.name,
                    'total_price': float(package.price)
                }
                result['total_price'] += package.price
            
            # Опциональные компоненты
            
            # Молдинг
            if molding_id and molding_consumption:
                molding = Molding.objects.get(pk=molding_id)
                molding_price = molding.price_per_meter * molding_consumption
                result['components']['molding'] = {
                    'name': molding.name,
                    'consumption': float(molding_consumption),
                    'unit_price': float(molding.price_per_meter),
                    'total_price': float(molding_price)
                }
                result['total_price'] += molding_price
                selected_material_types.append('molding')
            
            # Тросик
            if trosik_id and trosik_length:
                trosik = Trosik.objects.get(pk=trosik_id)
                trosik_price = trosik.price_per_meter * trosik_length
                result['components']['trosik'] = {
                    'name': trosik.name,
                    'length': float(trosik_length),
                    'unit_price': float(trosik.price_per_meter),
                    'total_price': float(trosik_price)
                }
                result['total_price'] += trosik_price
                selected_material_types.append('trosik')
            
            # Подвески
            if podveski_id and podveski_quantity:
                podveski = Podveski.objects.get(pk=podveski_id)
                podveski_price = podveski.price_per_unit * podveski_quantity
                result['components']['podveski'] = {
                    'name': podveski.name,
                    'quantity': podveski_quantity,
                    'unit_price': float(podveski.price_per_unit),
                    'total_price': float(podveski_price)
                }
                result['total_price'] += podveski_price
                selected_material_types.append('podveski')
            
            # Паспарту
            if passepartout_id:
                passepartout = Passepartout.objects.get(pk=passepartout_id)
                # Цена паспарту фиксированная, размеры используются только для информации
                result['components']['passepartout'] = {
                    'name': passepartout.name,
                    'length': float(passepartout_length) if passepartout_length else None,
                    'width': float(passepartout_width) if passepartout_width else None,
                    'total_price': float(passepartout.price)
                }
                result['total_price'] += passepartout.price
                selected_material_types.append('passepartout')
            
            # Натяжка
            if stretch_id:
                stretch = Stretch.objects.get(pk=stretch_id)
                stretch_calc = PriceCalculator.calculate_stretch_price(x1, x2, stretch)
                result['components']['stretch'] = {
                    'name': stretch.name,
                    'area': float(stretch_calc['area']),
                    'unit_price': float(stretch_calc['unit_price']),
                    'total_price': float(stretch_calc['total_price'])
                }
                result['total_price'] += stretch_calc['total_price']
                selected_material_types.append('stretch')
            
            # Работы - автоматически добавляем работы для выбранных материалов
            settings = WorkPriceSettings.get_settings()
            is_small = PriceCalculator.is_small_frame(x1, x2)
            
            # Если передан конкретный work_id, используем его
            if work_id:
                work = Work.objects.get(pk=work_id)
                work_price = work.price if is_small else work.price * settings.multiplier_for_large
                
                result['components']['work'] = {
                    'name': work.name,
                    'base_price': float(work.price),
                    'is_small_frame': is_small,
                    'multiplier': 1.0 if is_small else float(settings.multiplier_for_large),
                    'total_price': float(work_price)
                }
                result['total_price'] += work_price
            else:
                # Автоматически находим и добавляем работы для выбранных материалов
                auto_works = Work.objects.filter(material_type__in=selected_material_types)
                
                for idx, work in enumerate(auto_works):
                    work_price = work.price if is_small else work.price * settings.multiplier_for_large
                    
                    # Если несколько работ, добавляем индекс к ключу
                    work_key = 'work' if idx == 0 else f'work_{idx+1}'
                    
                    result['components'][work_key] = {
                        'name': work.name,
                        'material_type': work.material_type,
                        'base_price': float(work.price),
                        'is_small_frame': is_small,
                        'multiplier': 1.0 if is_small else float(settings.multiplier_for_large),
                        'total_price': float(work_price)
                    }
                    result['total_price'] += work_price
            
            result['total_price'] = float(result['total_price'])
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
