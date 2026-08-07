from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional, List, Any
from django.db.models import F

from .models import Baguette, Glass, Backing, Hardware, Podramnik, Package, Molding, Trosik, Podveski, Material, Passepartout, Stretch, TechOperation, Foamboard


def _dec(value, default='0') -> Decimal:
    if value is None or value == '':
        return Decimal(default)
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal(default)


def _okr(value) -> int:
    """Аналог 1С Окр(): округление до целого (half-up)."""
    return int(_dec(value).to_integral_value(rounding=ROUND_HALF_UP))


# Минимальная стоимость материала для клиента (пороги из кода 1С, процедура Расчет()):
# если расчётная стоимость меньше порога — берётся порог.
MIN_GLASS_PRICE = Decimal('30')
MIN_BACKING_PRICE = Decimal('20')
MIN_TROSIK_PRICE = Decimal('50')


def _floor(value: Decimal, minimum: Decimal) -> Decimal:
    """Порог снизу: возвращает minimum, если value <= minimum (как в 1С: >порог ? value : порог)."""
    value = _dec(value)
    return value if value > minimum else minimum


class PriceCalculator:
    """Класс для расчета стоимости заказа на раму"""

    @staticmethod
    def calculate_baguette_quantity(x1: Decimal, x2: Decimal, width: Decimal) -> Decimal:
        """
        Расчет количества багета по формуле: L + 8 * W,
        где L = 2 * (X1 + X2) в метрах, W - ширина багета в метрах.
        """
        # (X1 + X2) в см, переводим в метры
        perimeter = ((x1 + x2) * 2) / 100
        # Ширина багета хранится в метрах
        total = perimeter + 8 * width
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
    def normalize_length_to_meters(length: Decimal) -> Decimal:
        """
        Нормализация длины в метры.
        Значения больше 10 считаем введенными в сантиметрах и переводим в метры.
        """
        if length is None:
            return Decimal('0')
        if length > Decimal('10'):
            return length / Decimal('100')
        return length
    
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
            
            # Стекло (мин. MIN_GLASS_PRICE)
            if glass_id:
                glass = Glass.objects.get(pk=glass_id)
                glass_calc = PriceCalculator.calculate_glass_price(x1, x2, glass)
                glass_total = _floor(glass_calc['total_price'], MIN_GLASS_PRICE)
                result['components']['glass'] = {
                    'name': glass.name,
                    'area': float(glass_calc['area']),
                    'unit_price': float(glass_calc['unit_price']),
                    'total_price': float(glass_total)
                }
                result['total_price'] += glass_total
                selected_material_types.append('glass')

            # Подкладка (мин. MIN_BACKING_PRICE)
            if backing_id:
                backing = Backing.objects.get(pk=backing_id)
                backing_area = PriceCalculator.calculate_glass_area(x1, x2)
                backing_price = _floor(backing.price * backing_area, MIN_BACKING_PRICE)
                result['components']['backing'] = {
                    'name': backing.name,
                    'area': float(backing_area),
                    'unit_price': float(backing.price),
                    'total_price': float(backing_price)
                }
                result['total_price'] += backing_price
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
                podramnik_qty = PriceCalculator.calculate_baguette_quantity(x1, x2, Decimal('0'))
                podramnik_price = podramnik.price * podramnik_qty
                result['components']['podramnik'] = {
                    'name': podramnik.name,
                    'quantity': float(podramnik_qty),
                    'unit_price': float(podramnik.price),
                    'total_price': float(podramnik_price)
                }
                result['total_price'] += podramnik_price
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
            
            # Тросик (мин. MIN_TROSIK_PRICE)
            if trosik_id and trosik_length:
                trosik = Trosik.objects.get(pk=trosik_id)
                trosik_length_m = PriceCalculator.normalize_length_to_meters(trosik_length)
                trosik_price = _floor(trosik.price_per_meter * trosik_length_m, MIN_TROSIK_PRICE)
                result['components']['trosik'] = {
                    'name': trosik.name,
                    'length': float(trosik_length_m),
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
                pp_length = passepartout_length if passepartout_length else x1
                pp_width = passepartout_width if passepartout_width else x2
                pp_area = PriceCalculator.calculate_glass_area(pp_length, pp_width)
                pp_price = passepartout.price * pp_area
                result['components']['passepartout'] = {
                    'name': passepartout.name,
                    'length': float(pp_length),
                    'width': float(pp_width),
                    'area': float(pp_area),
                    'unit_price': float(passepartout.price),
                    'total_price': float(pp_price)
                }
                result['total_price'] += pp_price
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
            
            # Работы больше НЕ входят в цену: технологические операции считаются
            # справочно в OrderExtrasCalculator (по данным 1С), а стоимость сборки
            # учитывается через «Сложность рамы/паспарту/крепления». Параметры
            # work_id / selected_material_types оставлены для обратной совместимости
            # входных данных, но на цену не влияют.
            _ = (work_id, selected_material_types)

            result['total_price'] = float(result['total_price'])
            
        except Exception as e:
            result['error'] = str(e)
        
        return result


class OrderExtrasCalculator:
    """
    Автосложность (входит в цену) и технологические операции / «работы» (справочно).

    Повторяет логику 1С: Расчет() (блок сложности) и ЗаполнитьРаботу().
    Сложность рамы/паспарту/крепления добавляется в цену заказа.
    Работы подбираются по диапазону размеров (макс. стороны рамы 1) либо по спец-формуле
    и НЕ входят в цену — считаются справочно (сумма расценок + время = Σрасценка / 100).
    """

    @staticmethod
    def _frame_infos(frames: List[Dict], gx1: Decimal, gx2: Decimal, data: Dict) -> List[Dict]:
        fr = [f for f in (frames or []) if f.get('baguette_id')]
        if not fr and data.get('baguette_id'):
            fr = [{'baguette_id': data['baguette_id'], 'x1': gx1, 'x2': gx2}]
        # Багет опционален: если он не выбран, но заданы размеры — рама всё равно
        # изготавливается, поэтому считаем одну раму по размерам (ширина багета = 0).
        if not fr and gx1 > 0 and gx2 > 0:
            fr = [{'baguette_id': None, 'x1': gx1, 'x2': gx2}]
        infos = []
        for f in fr:
            fx1 = _dec(f.get('x1') or gx1)
            fx2 = _dec(f.get('x2') or gx2)
            if fx1 <= 0 or fx2 <= 0:
                fx1, fx2 = gx1, gx2
            baguette = Baguette.objects.filter(pk=f['baguette_id']).first()
            width = baguette.width if baguette else Decimal('0')
            infos.append({'x1': fx1, 'x2': fx2, 'width': width, 'max': max(fx1, fx2)})
        return infos

    @classmethod
    def compute(cls, *, frames, passepartouts, x1, x2, data) -> Dict[str, Any]:
        gx1, gx2 = _dec(x1), _dec(x2)
        q = int(data.get('quantity') or 1) or 1
        infos = cls._frame_infos(frames, gx1, gx2, data)
        n = len(infos)

        # Опорный размер рамы 1 (макс(бд1, бш1)) — для сложности и подбора работ паспарту/стекла/подкладки.
        if infos:
            b1x, b1y = infos[0]['x1'], infos[0]['x2']
        else:
            b1x, b1y = gx1, gx2
        base_max = max(b1x, b1y)

        # ---------- Сложность рамы (СложностьР) ----------
        R1 = (infos[0]['width'] * 2000) if n >= 1 else Decimal('0')
        R2 = (infos[1]['width'] * 2000) if n >= 2 else Decimal('0')
        R3 = (infos[2]['width'] * 2000) if n >= 3 else Decimal('0')
        R4 = Decimal('50') if (n >= 1 and (b1x < 15 or b1y < 15)) else Decimal('0')

        hw_qty = _dec(data.get('hardware_quantity'))
        F_ = (hw_qty * 10) if (data.get('hardware_id') and hw_qty > 0) else Decimal('0')

        RB = R1 + R2 + R3 + R4 + F_

        def bump(v120, v75):
            if b1x >= 120 or b1y >= 120:
                return Decimal(v120)
            if b1x >= 75 or b1y >= 75:
                return Decimal(v75)
            return Decimal('0')

        if data.get('backing_id'):
            RB += bump('50', '30')
        if data.get('foamboard_id'):
            RB += bump('50', '30')
        if data.get('glass_id'):
            RB += bump('100', '60')
        if data.get('podramnik_id'):
            if b1x >= 160 or b1y >= 160:
                RB += Decimal('120')
            elif b1x >= 120 or b1y >= 120:
                RB += Decimal('100')
            elif b1x >= 80 or b1y >= 80:
                RB += Decimal('80')
            else:
                RB += Decimal('60')

        RD = _dec(data.get('extra_frame_complexity'))
        compR = Decimal('100')
        if RB > 0 and RD > 0:
            compR = 100 + RB + RD
        elif RB == 0 and RD > 0:
            compR = 100 + RD
        elif RB > 0 and RD == 0:
            compR = 100 + RB

        # ---------- Сложность паспарту (СложностьП) ----------
        npp = len([p for p in (passepartouts or []) if p.get('passepartout_id')])
        P2 = Decimal('40') if npp >= 3 else Decimal('0')
        P1 = Decimal('30') if npp >= 2 else Decimal('0')
        windows = int(data.get('passepartout_windows') or 0)
        Pkop = Decimal(windows * 30) if windows > 1 else Decimal('0')
        PP = P1 + P2 + Pkop
        PD = _dec(data.get('extra_pp_complexity'))
        compP = Decimal('0')
        if PD > 0 and PP > 0:
            compP = PD + PP
        elif PD == 0 and PP > 0:
            compP = PP
        elif PD > 0 and PP == 0:
            compP = PD

        # ---------- Сложность крепления объекта (СложностьКрОбТ) ----------
        mount = int(data.get('mount_count') or 0)
        compMount = Decimal(mount * 20) if mount > 0 else Decimal('0')

        # ---------- Работы (справочно) ----------
        works: List[Dict] = []

        def add_work(op_type, size, label=None, rate_override=None):
            if rate_override is not None:
                rate = _dec(rate_override)
                name = label or op_type
            else:
                op = TechOperation.find_by_size(op_type, size)
                if not op or op.rate is None:
                    return
                rate = op.rate
                name = label or op.name
            total = rate * q
            works.append({
                'operation_type': op_type,
                'name': name,
                'rate': float(rate),
                'quantity': q,
                'total': float(total),
            })

        # Рама: тип работы = число рам (1→рама, 2→двойная, 3→тройная), размер внешней рамы
        if n == 1:
            add_work('rama', infos[0]['max'])
        elif n == 2:
            add_work('rama2', infos[1]['max'])
        elif n >= 3:
            add_work('rama3', infos[2]['max'])

        # Паспарту 1/2/3 — по опорному размеру рамы 1
        pp_types = ['passepartout', 'passepartout2', 'passepartout3']
        pp_list = [p for p in (passepartouts or []) if p.get('passepartout_id')]
        for i, _p in enumerate(pp_list[:3]):
            add_work(pp_types[i], base_max)

        if data.get('backing_id'):
            add_work('backing', base_max)
        if data.get('glass_id'):
            add_work('glass', base_max)
        if data.get('podramnik_id'):
            add_work('podramnik', base_max)
        if data.get('foamboard_id'):
            add_work('foamboard', base_max)
        if data.get('molding_id'):
            add_work('molding', 0)  # фиксированная расценка

        # Натяжка: расценка из справочника по размеру (макс. сторона рамы),
        # как у остальных работ. Площадь/склад считаются отдельно по кв.м.
        if data.get('stretch_id'):
            add_work('stretch', base_max, label='Натяжка')

        # Упаковка: расценка = Окр(цена_упаковки / 2)
        if data.get('package_id'):
            package = Package.objects.filter(pk=data['package_id']).first()
            if package:
                add_work('package', 0, label='Упаковка', rate_override=_okr(package.price / 2))

        # Сложности как работы = сложность / 2
        if compR > 0:
            add_work('complexity_frame', 0, label='Сложность рамы', rate_override=_okr(compR / 2))
        if compP > 0:
            add_work('complexity_pp', 0, label='Сложность паспарту', rate_override=_okr(compP / 2))
        if compMount > 0:
            add_work('complexity_mount', 0, label='Сложность крепления', rate_override=_okr(compMount / 2))

        total_rate = sum(w['total'] for w in works)

        return {
            'manual_complexity': float(_dec(data.get('manual_complexity'))),
            'complexity': {
                'frame': float(compR * q),
                'passepartout': float(compP * q),
                'mount': float(compMount * q),
                'total': float((compR + compP + compMount) * q),
            },
            'works': {
                'items': works,
                'total_rate': float(total_rate),
                'work_time_hours': round(total_rate / 100, 2),
            },
        }

    @classmethod
    def for_order(cls, order, frames: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Считает сложность и работы для сохранённого заказа (для квитанции/детализации)."""
        frames = frames or []
        extras_frames = []
        for f in frames:
            if isinstance(f, dict):
                extras_frames.append({
                    'baguette_id': f.get('baguette_id'),
                    'x1': f.get('x1') or order.x1,
                    'x2': f.get('x2') or order.x2,
                })
        if not extras_frames:
            extras_frames = [{'baguette_id': order.baguette_id, 'x1': order.x1, 'x2': order.x2}]

        pps = []
        if frames and isinstance(frames[0], dict):
            embedded = frames[0].get('passepartouts')
            if isinstance(embedded, list):
                pps.extend([p for p in embedded if isinstance(p, dict) and p.get('passepartout_id')])
        for f in frames:
            if isinstance(f, dict) and f.get('passepartout_id'):
                pps.append({
                    'passepartout_id': f.get('passepartout_id'),
                    'passepartout_length': f.get('passepartout_length'),
                    'passepartout_width': f.get('passepartout_width'),
                })
        if not pps and order.passepartout_id:
            pps.append({
                'passepartout_id': order.passepartout_id,
                'passepartout_length': order.passepartout_length,
                'passepartout_width': order.passepartout_width,
            })

        data = {
            'baguette_id': order.baguette_id,
            'glass_id': order.glass_id,
            'backing_id': order.backing_id,
            'hardware_id': order.hardware_id,
            'hardware_quantity': order.hardware_quantity,
            'podramnik_id': order.podramnik_id,
            'molding_id': order.molding_id,
            'package_id': order.package_id,
            'stretch_id': order.stretch_id,
            'manual_complexity': order.manual_complexity,
            'quantity': 1,
        }
        return cls.compute(frames=extras_frames, passepartouts=pps, x1=order.x1, x2=order.x2, data=data)

    @staticmethod
    def apply(calculation: Dict, extras: Dict) -> Dict:
        """
        Включает работы в стоимость заказа (все работы оплачивает клиент).
        Сложность рамы/паспарту/крепления входит в цену как соответствующая
        работа (сложность / 2), поэтому отдельной строкой полной сложности
        в цену не добавляется (иначе было бы задвоение).
        """
        works = extras['works']
        manual = extras.get('manual_complexity') or 0
        total = float(calculation.get('total_price', 0)) + works['total_rate'] + manual
        if manual > 0:
            calculation.setdefault('components', {})['manual_complexity'] = {
                'name': 'Сложность', 'total_price': manual
            }
        calculation['total_price'] = total
        calculation['works'] = works
        return calculation


class StockDeduction:
    """Списание материалов со склада при создании заказа"""

    @staticmethod
    def deduct_from_order(order_data: Dict[str, Any], frames: List[Dict], passepartouts: Optional[List[Dict]] = None) -> None:
        """
        Списывает материалы со склада на основе данных заказа.
        Использует F() для атомарного обновления (защита от гонок).
        """
        x1 = order_data.get('x1') or Decimal('0')
        x2 = order_data.get('x2') or Decimal('0')

        # Багет: по каждой раме свой багет и размеры
        baguette_consumption: Dict[int, Decimal] = {}
        passepartout_consumption: Dict[int, Decimal] = {}

        if frames:
            for frame in frames:
                if frame.get('baguette_id'):
                    fx1 = Decimal(str(frame.get('x1', x1))) if frame.get('x1') else x1
                    fx2 = Decimal(str(frame.get('x2', x2))) if frame.get('x2') else x2
                    if fx1 <= 0 or fx2 <= 0:
                        fx1, fx2 = x1, x2
                    baguette = Baguette.objects.filter(pk=frame['baguette_id']).first()
                    if baguette:
                        qty = PriceCalculator.calculate_baguette_quantity(fx1, fx2, baguette.width)
                        bid = baguette.pk
                        baguette_consumption[bid] = baguette_consumption.get(bid, Decimal('0')) + qty

                if frame.get('passepartout_id'):
                    pid = frame['passepartout_id']
                    fx1 = Decimal(str(frame.get('x1', x1))) if frame.get('x1') else x1
                    fx2 = Decimal(str(frame.get('x2', x2))) if frame.get('x2') else x2
                    pp_length = Decimal(str(frame.get('passepartout_length'))) if frame.get('passepartout_length') else fx1
                    pp_width = Decimal(str(frame.get('passepartout_width'))) if frame.get('passepartout_width') else fx2
                    pp_area = PriceCalculator.calculate_glass_area(pp_length, pp_width)
                    passepartout_consumption[pid] = passepartout_consumption.get(pid, Decimal('0')) + pp_area
        else:
            # Одна рама
            if order_data.get('baguette_id'):
                baguette = Baguette.objects.filter(pk=order_data['baguette_id']).first()
                if baguette:
                    qty = PriceCalculator.calculate_baguette_quantity(x1, x2, baguette.width)
                    baguette_consumption[baguette.pk] = qty
            if order_data.get('passepartout_id'):
                pp_length = Decimal(str(order_data.get('passepartout_length'))) if order_data.get('passepartout_length') else x1
                pp_width = Decimal(str(order_data.get('passepartout_width'))) if order_data.get('passepartout_width') else x2
                passepartout_consumption[order_data['passepartout_id']] = PriceCalculator.calculate_glass_area(pp_length, pp_width)

        # Новый формат: отдельный список паспарту (независимо от рам)
        if passepartouts:
            for pp in passepartouts:
                pid = pp.get('passepartout_id')
                if not pid:
                    continue
                pp_length = Decimal(str(pp.get('passepartout_length'))) if pp.get('passepartout_length') else x1
                pp_width = Decimal(str(pp.get('passepartout_width'))) if pp.get('passepartout_width') else x2
                pp_area = PriceCalculator.calculate_glass_area(pp_length, pp_width)
                passepartout_consumption[pid] = passepartout_consumption.get(pid, Decimal('0')) + pp_area

        # Списание багета
        for bid, qty in baguette_consumption.items():
            Baguette.objects.filter(pk=bid).update(stock_quantity=F('stock_quantity') - qty)

        # Площадь стекла (все рамы)
        if frames:
            frame_sizes = []
            for f in frames:
                if f.get('baguette_id'):
                    fx1 = Decimal(str(f.get('x1', x1))) if f.get('x1') else x1
                    fx2 = Decimal(str(f.get('x2', x2))) if f.get('x2') else x2
                    if fx1 > 0 and fx2 > 0:
                        frame_sizes.append((fx1, fx2))
            if not frame_sizes:
                frame_sizes = [(x1, x2)]
            total_glass_area = sum(PriceCalculator.calculate_glass_area(a, b) for a, b in frame_sizes)
        else:
            total_glass_area = PriceCalculator.calculate_glass_area(x1, x2)

        # Стекло
        if order_data.get('glass_id') and total_glass_area > 0:
            Glass.objects.filter(pk=order_data['glass_id']).update(
                stock_quantity=F('stock_quantity') - total_glass_area
            )

        # Подкладка (по площади)
        if order_data.get('backing_id') and total_glass_area > 0:
            Backing.objects.filter(pk=order_data['backing_id']).update(
                stock_quantity=F('stock_quantity') - total_glass_area
            )

        # Фурнитура
        if order_data.get('hardware_id'):
            hq = order_data.get('hardware_quantity') or 1
            Hardware.objects.filter(pk=order_data['hardware_id']).update(
                stock_quantity=F('stock_quantity') - hq
            )

        # Подрамник (как по раме - погонные метры)
        if order_data.get('podramnik_id'):
            if frames:
                total_podramnik_qty = Decimal('0')
                for f in frames:
                    if f.get('baguette_id'):
                        fx1 = Decimal(str(f.get('x1', x1))) if f.get('x1') else x1
                        fx2 = Decimal(str(f.get('x2', x2))) if f.get('x2') else x2
                        if fx1 > 0 and fx2 > 0:
                            total_podramnik_qty += PriceCalculator.calculate_baguette_quantity(fx1, fx2, Decimal('0'))
                if total_podramnik_qty <= 0:
                    total_podramnik_qty = PriceCalculator.calculate_baguette_quantity(x1, x2, Decimal('0'))
            else:
                total_podramnik_qty = PriceCalculator.calculate_baguette_quantity(x1, x2, Decimal('0'))
            Podramnik.objects.filter(pk=order_data['podramnik_id']).update(
                stock_quantity=F('stock_quantity') - total_podramnik_qty
            )

        # Упаковка (1 шт)
        if order_data.get('package_id'):
            Package.objects.filter(pk=order_data['package_id']).update(
                stock_quantity=F('stock_quantity') - 1
            )

        # Паспарту
        for pid, qty in passepartout_consumption.items():
            Passepartout.objects.filter(pk=pid).update(
                stock_quantity=F('stock_quantity') - qty
            )

        # Молдинг
        if order_data.get('molding_id') and order_data.get('molding_consumption'):
            Molding.objects.filter(pk=order_data['molding_id']).update(
                stock_quantity=F('stock_quantity') - order_data['molding_consumption']
            )

        # Тросик
        if order_data.get('trosik_id') and order_data.get('trosik_length'):
            trosik_length_m = PriceCalculator.normalize_length_to_meters(Decimal(str(order_data['trosik_length'])))
            Trosik.objects.filter(pk=order_data['trosik_id']).update(
                stock_quantity=F('stock_quantity') - trosik_length_m
            )

        # Подвески
        if order_data.get('podveski_id') and order_data.get('podveski_quantity'):
            Podveski.objects.filter(pk=order_data['podveski_id']).update(
                stock_quantity=F('stock_quantity') - order_data['podveski_quantity']
            )

        # Натяжка (если используется вместо стекла — в данных может быть stretch_id)
        stretch_id = order_data.get('stretch_id')
        if stretch_id and total_glass_area > 0:
            Stretch.objects.filter(pk=stretch_id).update(
                stock_quantity=F('stock_quantity') - total_glass_area
            )
