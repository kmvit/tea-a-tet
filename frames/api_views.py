from rest_framework.decorators import api_view
from rest_framework.response import Response
from decimal import Decimal
import json
from django.db.models import Q
from django.http import HttpResponse

from .models import (
    Baguette, Glass, Backing, Hardware, Podramnik, Package,
    Molding, Trosik, Podveski, Passepartout, Stretch, Foamboard, TechOperation
)
from .services import (
    PriceCalculator, StockDeduction, OrderExtrasCalculator,
    _floor, MIN_GLASS_PRICE, MIN_BACKING_PRICE,
)
from orders.models import Order


def _collect_backing_ids(data, frames):
    """Собирает id подкладок (несколько) из запроса и/или сохранённых frames_data."""
    ids = []

    def _add(seq):
        if isinstance(seq, list):
            for b in seq:
                bid = b.get('backing_id') if isinstance(b, dict) else b
                if bid:
                    ids.append(bid)

    _add(data.get('backings'))
    if frames and isinstance(frames[0], dict):
        _add(frames[0].get('backings'))
    if not ids and data.get('backing_id'):
        ids.append(data.get('backing_id'))

    seen, out = set(), []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def _collect_passepartouts(passepartouts_data, frames):
    """Собирает список паспарту из нового формата и legacy-данных рам."""
    items = []

    if isinstance(passepartouts_data, list):
        for pp in passepartouts_data:
            if isinstance(pp, dict) and pp.get('passepartout_id'):
                items.append(pp)

    if frames:
        # Новый формат может храниться внутри первой рамы в frames_data
        embedded = frames[0].get('passepartouts') if isinstance(frames[0], dict) else None
        if isinstance(embedded, list):
            for pp in embedded:
                if isinstance(pp, dict) and pp.get('passepartout_id'):
                    items.append(pp)

        # Legacy: паспарту было привязано к каждой раме
        for frame in frames:
            if isinstance(frame, dict) and frame.get('passepartout_id'):
                items.append({
                    'passepartout_id': frame.get('passepartout_id'),
                    'passepartout_length': frame.get('passepartout_length'),
                    'passepartout_width': frame.get('passepartout_width'),
                })

    return items


# Похожие латинские/кириллические буквы приводим к одному виду,
# чтобы «M59» находил «М59» (кириллица) и наоборот.
_LOOKALIKE = str.maketrans({
    'a': 'а', 'b': 'в', 'c': 'с', 'e': 'е', 'h': 'н', 'k': 'к', 'm': 'м',
    'o': 'о', 'p': 'р', 't': 'т', 'x': 'х', 'y': 'у',
})


def _norm_search(s):
    """Нормализация для поиска: без пробелов, в нижнем регистре, латиница→кириллица."""
    return (s or '').replace(' ', '').lower().translate(_LOOKALIKE)


@api_view(['GET'])
def get_baguettes(request):
    """API для получения списка багетов с поддержкой поиска"""
    query = request.GET.get('search', '').strip()

    baguettes = list(Baguette.objects.all())

    # Поиск по названию или штрихкоду — без учёта пробелов, регистра и латиница/кириллица
    if query:
        q = _norm_search(query)
        baguettes = [
            b for b in baguettes
            if q in _norm_search(b.name) or q in _norm_search(b.barcode or '')
        ]

    data = []
    for baguette in baguettes:
        image_url = None
        if baguette.image:
            image_url = request.build_absolute_uri(baguette.image.url)
        data.append({
            'id': baguette.pk,
            'name': baguette.name,
            'barcode': baguette.barcode or '',
            'width': float(baguette.width),
            'price': float(baguette.price),
            'stock_quantity': float(baguette.stock_quantity),
            'image': image_url,
        })
    return Response(data)


@api_view(['GET'])
def get_glasses(request):
    """API для получения списка стекол"""
    glasses = Glass.objects.all()
    data = []
    for glass in glasses:
        data.append({
            'id': glass.pk,
            'name': glass.name,
            'price_per_sqm': float(glass.price_per_sqm),
        })
    return Response(data)


@api_view(['GET'])
def get_backings(request):
    """API для получения списка подкладок"""
    backings = Backing.objects.all()
    data = []
    for backing in backings:
        data.append({
            'id': backing.pk,
            'name': backing.name,
            'price': float(backing.price),
        })
    return Response(data)


@api_view(['GET'])
def get_hardware(request):
    """API для получения списка фурнитуры"""
    hardware_list = Hardware.objects.all()
    data = []
    for hardware in hardware_list:
        data.append({
            'id': hardware.pk,
            'name': hardware.name,
            'price_per_unit': float(hardware.price_per_unit),
        })
    return Response(data)


@api_view(['GET'])
def get_podramniki(request):
    """API для получения списка подрамников"""
    podramniki = Podramnik.objects.all()
    data = []
    for podramnik in podramniki:
        data.append({
            'id': podramnik.pk,
            'name': podramnik.name,
            'price': float(podramnik.price),
        })
    return Response(data)


@api_view(['GET'])
def get_packages(request):
    """API для получения списка упаковок"""
    packages = Package.objects.all()
    data = []
    for package in packages:
        data.append({
            'id': package.pk,
            'name': package.name,
            'price': float(package.price),
        })
    return Response(data)


@api_view(['GET'])
def get_moldings(request):
    """API для получения списка молдингов"""
    moldings = Molding.objects.all()
    data = []
    for molding in moldings:
        data.append({
            'id': molding.pk,
            'name': molding.name,
            'price_per_meter': float(molding.price_per_meter),
        })
    return Response(data)


@api_view(['GET'])
def get_trosiki(request):
    """API для получения списка тросиков"""
    trosiki = Trosik.objects.all()
    data = []
    for trosik in trosiki:
        data.append({
            'id': trosik.pk,
            'name': trosik.name,
            'price_per_meter': float(trosik.price_per_meter),
        })
    return Response(data)


@api_view(['GET'])
def get_podveski(request):
    """API для получения списка подвесок"""
    podveski = Podveski.objects.all()
    data = []
    for podveska in podveski:
        data.append({
            'id': podveska.pk,
            'name': podveska.name,
            'price_per_unit': float(podveska.price_per_unit),
        })
    return Response(data)


@api_view(['GET'])
def get_passepartout(request):
    """API для получения списка паспарту"""
    passepartout_list = Passepartout.objects.all()
    data = []
    for passepartout in passepartout_list:
        image_url = None
        if passepartout.image:
            image_url = request.build_absolute_uri(passepartout.image.url)
        data.append({
            'id': passepartout.pk,
            'name': passepartout.name,
            'price': float(passepartout.price),
            'image': image_url,
        })
    return Response(data)


@api_view(['GET'])
def get_stretches(request):
    """API для получения списка натяжек"""
    stretches = Stretch.objects.all()
    data = []
    for stretch in stretches:
        data.append({
            'id': stretch.pk,
            'name': stretch.name,
            'price_per_meter': float(stretch.price_per_meter),
        })
    return Response(data)


@api_view(['GET'])
def get_foamboards(request):
    """API для получения списка пенокартона (накатка)"""
    data = []
    for fb in Foamboard.objects.all():
        data.append({
            'id': fb.pk,
            'name': fb.name,
            'price': float(fb.price),
        })
    return Response(data)


@api_view(['GET'])
def get_works(request):
    """API для получения справочника технологических операций (работ)"""
    data = []
    for op in TechOperation.objects.all():
        data.append({
            'id': op.pk,
            'code': op.code,
            'operation_type': op.operation_type,
            'name': op.name,
            'size_from': float(op.size_from) if op.size_from is not None else None,
            'size_to': float(op.size_to) if op.size_to is not None else None,
            'rate': float(op.rate) if op.rate is not None else None,
        })
    return Response(data)


@api_view(['POST'])
def calculate_price_api(request):
    """API для расчета цены заказа"""
    try:
        data = request.data
        
        # Получаем данные для расчета
        x1 = Decimal(str(data.get('x1', 0))) if data.get('x1') else Decimal('0')
        x2 = Decimal(str(data.get('x2', 0))) if data.get('x2') else Decimal('0')
        
        # Проверяем, есть ли массив рамок
        frames = data.get('frames', [])
        passepartouts = _collect_passepartouts(data.get('passepartouts', []), frames)
        backing_ids = _collect_backing_ids(data, frames)

        if frames and len(frames) > 0:
            # Для нескольких рам — x1, x2 могут быть в каждой раме
            has_valid_sizes = x1 and x2 and x1 > 0 and x2 > 0
            frames_have_sizes = all(
                frame.get('x1') and frame.get('x2') and
                Decimal(str(frame.get('x1', 0))) > 0 and Decimal(str(frame.get('x2', 0))) > 0
                for frame in frames if frame.get('baguette_id')
            )
            if not has_valid_sizes and not frames_have_sizes:
                return Response({'error': 'Необходимо указать размеры x1 и x2 (глобально или для каждой рамы)'}, status=400)
        elif not x1 or not x2 or x1 <= 0 or x2 <= 0:
            return Response({'error': 'Необходимо указать размеры x1 и x2'}, status=400)
        
        # Если есть массив рамок, рассчитываем для каждой
        if frames and len(frames) > 0:
            result = {
                'components': {},
                'total_price': Decimal('0')
            }
            
            # Рассчитываем цену для каждой рамы (багет, паспарту, работа привязаны к раме)
            for idx, frame in enumerate(frames):
                if frame.get('baguette_id'):
                    # Используем размеры рамы, если заданы; иначе — глобальные x1, x2
                    fx1 = Decimal(str(frame.get('x1', x1))) if frame.get('x1') else x1
                    fx2 = Decimal(str(frame.get('x2', x2))) if frame.get('x2') else x2
                    if not fx1 or not fx2 or fx1 <= 0 or fx2 <= 0:
                        fx1, fx2 = x1, x2
                    frame_calculation = PriceCalculator.calculate_total_price(
                        x1=fx1,
                        x2=fx2,
                        baguette_id=frame.get('baguette_id'),
                        work_id=frame.get('work_id'),
                    )
                    
                    # Добавляем компоненты рамы с префиксом номера (багет, паспарту, работа)
                    frame_num = idx + 1
                    for key, value in frame_calculation.get('components', {}).items():
                        if key in ['baguette', 'passepartout', 'work']:
                            component_key = f'{key}_frame{frame_num}'
                            result['components'][component_key] = {
                                **value,
                                'name': f"{value.get('name', key)} (Рама {frame_num})"
                            }
                            result['total_price'] += Decimal(str(value.get('total_price', 0)))

            # Паспарту: независимая группировка (до 3 шт)
            for pp_idx, pp_data in enumerate(passepartouts):
                pp_id = pp_data.get('passepartout_id')
                if not pp_id:
                    continue
                passepartout = Passepartout.objects.get(pk=pp_id)
                pp_length = Decimal(str(pp_data.get('passepartout_length'))) if pp_data.get('passepartout_length') else x1
                pp_width = Decimal(str(pp_data.get('passepartout_width'))) if pp_data.get('passepartout_width') else x2
                pp_area = PriceCalculator.calculate_glass_area(pp_length, pp_width)
                pp_price = pp_area * passepartout.price
                result['components'][f'passepartout_{pp_idx + 1}'] = {
                    'name': f'{passepartout.name} (Паспарту {pp_idx + 1})',
                    'length': float(pp_length),
                    'width': float(pp_width),
                    'area': float(pp_area),
                    'unit_price': float(passepartout.price),
                    'total_price': float(pp_price),
                }
                result['total_price'] += pp_price
            
            # Для стекла/натяжки: при разных размерах рам суммируем площади
            # Определяем размеры для расчёта общих компонентов
            frame_sizes = []
            for frame in frames:
                if frame.get('baguette_id'):
                    fx1 = Decimal(str(frame.get('x1', x1))) if frame.get('x1') else x1
                    fx2 = Decimal(str(frame.get('x2', x2))) if frame.get('x2') else x2
                    if fx1 and fx2 and fx1 > 0 and fx2 > 0:
                        frame_sizes.append((fx1, fx2))
            if not frame_sizes:
                frame_sizes = [(x1, x2)] if x1 and x2 else []

            # Используем первую пару размеров только для компонентов, которые не зависят от суммирования рам
            eff_x1, eff_x2 = frame_sizes[0] if frame_sizes else (x1, x2)
            other_calculation = PriceCalculator.calculate_total_price(
                x1=eff_x1,
                x2=eff_x2,
                glass_id=None,
                backing_id=None,
                hardware_id=data.get('hardware_id'),
                hardware_quantity=data.get('hardware_quantity', 1),
                podramnik_id=data.get('podramnik_id'),
                package_id=data.get('package_id'),
                package_quantity=data.get('package_quantity', 1),
                molding_id=data.get('molding_id'),
                molding_consumption=Decimal(str(data.get('molding_consumption'))) if data.get('molding_consumption') else None,
                trosik_id=data.get('trosik_id'),
                trosik_length=Decimal(str(data.get('trosik_length'))) if data.get('trosik_length') else None,
                podveski_id=data.get('podveski_id'),
                podveski_quantity=data.get('podveski_quantity'),
                stretch_id=None,
            )

            # Стекло — по суммарной площади, если рам несколько с разными размерами.
            # Натяжка здесь НЕ считается: это работа мастера по периметру,
            # учитывается в OrderExtrasCalculator (ниже, через apply()).
            from frames.models import Glass
            total_glass_area = sum(
                PriceCalculator.calculate_glass_area(fx1, fx2) for fx1, fx2 in frame_sizes
            )
            if data.get('glass_id') and total_glass_area > 0:
                glass = Glass.objects.get(pk=data['glass_id'])
                glass_calc = {
                    'area': float(total_glass_area),
                    'unit_price': float(glass.price_per_sqm),
                    'total_price': float(_floor(total_glass_area * glass.price_per_sqm, MIN_GLASS_PRICE))
                }
                result['components']['glass'] = {
                    'name': glass.name,
                    **glass_calc
                }
                result['total_price'] += Decimal(str(glass_calc['total_price']))

            # Подкладка/подрамник — «на картину», один раз по раме меньшего размера
            pic_x1, pic_x2 = min(frame_sizes, key=lambda s: s[0] * s[1]) if frame_sizes else (x1, x2)
            pic_area = PriceCalculator.calculate_glass_area(pic_x1, pic_x2)

            # Подкладки (несколько) — по площади рамы меньшего размера
            if backing_ids and pic_area > 0:
                b_comps, b_total = PriceCalculator.price_backings(backing_ids, pic_area)
                result['components'].update(b_comps)
                result['total_price'] += b_total

            # Подрамник — один раз по раме меньшего размера
            if data.get('podramnik_id'):
                podramnik = Podramnik.objects.get(pk=data['podramnik_id'])
                podramnik_qty = PriceCalculator.calculate_baguette_quantity(pic_x1, pic_x2, Decimal('0'))
                podramnik_price = podramnik_qty * podramnik.price
                result['components']['podramnik'] = {
                    'name': podramnik.name,
                    'quantity': float(podramnik_qty),
                    'unit_price': float(podramnik.price),
                    'total_price': float(podramnik_price),
                }
                result['total_price'] += Decimal(str(podramnik_price))

            # Добавляем остальные компоненты (без glass и stretch — они уже добавлены)
            for key, value in other_calculation.get('components', {}).items():
                if key not in ('glass', 'stretch', 'backing', 'podramnik'):
                    result['components'][key] = value
                    result['total_price'] += Decimal(str(value.get('total_price', 0)))
            
            result['total_price'] = float(result['total_price'])
            extras = OrderExtrasCalculator.compute(
                frames=frames, passepartouts=passepartouts, x1=eff_x1, x2=eff_x2, data=data
            )
            OrderExtrasCalculator.apply(result, extras, quantity=data.get('quantity', 1))
            return Response(result)
        else:
            # Обратная совместимость: расчет для одной рамы
            calculation = PriceCalculator.calculate_total_price(
                x1=x1,
                x2=x2,
                baguette_id=data.get('baguette_id'),
                glass_id=data.get('glass_id'),
                backing_id=data.get('backing_id'),
                backing_ids=backing_ids,
                hardware_id=data.get('hardware_id'),
                hardware_quantity=data.get('hardware_quantity', 1),
                podramnik_id=data.get('podramnik_id'),
                package_id=data.get('package_id'),
                package_quantity=data.get('package_quantity', 1),
                molding_id=data.get('molding_id'),
                molding_consumption=Decimal(str(data.get('molding_consumption'))) if data.get('molding_consumption') else None,
                trosik_id=data.get('trosik_id'),
                trosik_length=Decimal(str(data.get('trosik_length'))) if data.get('trosik_length') else None,
                podveski_id=data.get('podveski_id'),
                podveski_quantity=data.get('podveski_quantity'),
                passepartout_id=data.get('passepartout_id'),
                passepartout_length=Decimal(str(data.get('passepartout_length'))) if data.get('passepartout_length') else None,
                passepartout_width=Decimal(str(data.get('passepartout_width'))) if data.get('passepartout_width') else None,
                stretch_id=data.get('stretch_id'),
                work_id=data.get('work_id'),
            )
            if passepartouts:
                for pp_idx, pp_data in enumerate(passepartouts):
                    pp_id = pp_data.get('passepartout_id')
                    if not pp_id:
                        continue
                    passepartout = Passepartout.objects.get(pk=pp_id)
                    pp_length = Decimal(str(pp_data.get('passepartout_length'))) if pp_data.get('passepartout_length') else x1
                    pp_width = Decimal(str(pp_data.get('passepartout_width'))) if pp_data.get('passepartout_width') else x2
                    pp_area = PriceCalculator.calculate_glass_area(pp_length, pp_width)
                    pp_price = pp_area * passepartout.price
                    calculation['components'][f'passepartout_{pp_idx + 1}'] = {
                        'name': f'{passepartout.name} (Паспарту {pp_idx + 1})',
                        'length': float(pp_length),
                        'width': float(pp_width),
                        'area': float(pp_area),
                        'unit_price': float(passepartout.price),
                        'total_price': float(pp_price),
                    }
                    calculation['total_price'] += float(pp_price)

            single_frames = [{'baguette_id': data.get('baguette_id'), 'x1': x1, 'x2': x2}] if data.get('baguette_id') else []
            extras = OrderExtrasCalculator.compute(
                frames=single_frames, passepartouts=passepartouts, x1=x1, x2=x2, data=data
            )
            OrderExtrasCalculator.apply(calculation, extras, quantity=data.get('quantity', 1))
            return Response(calculation)

    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
def create_order_api(request):
    """API для создания заказа"""
    try:
        data = request.data
        
        # Проверяем наличие массив рамок
        frames = data.get('frames', [])
        passepartouts = _collect_passepartouts(data.get('passepartouts', []), frames)
        backing_ids = _collect_backing_ids(data, frames)

        # Определяем данные для заказа
        # Если есть массив рамок, берем первую раму для сохранения в Order (модель поддерживает только одну раму)
        # Но рассчитываем цену для всех рамок
        if frames and len(frames) > 0:
            first_frame = frames[0]
            baguette_id = first_frame.get('baguette_id')
            if passepartouts:
                first_pp = passepartouts[0]
                passepartout_id = first_pp.get('passepartout_id')
                passepartout_length = first_pp.get('passepartout_length')
                passepartout_width = first_pp.get('passepartout_width')
            else:
                passepartout_id = first_frame.get('passepartout_id')
                passepartout_length = first_frame.get('passepartout_length')
                passepartout_width = first_frame.get('passepartout_width')
        else:
            # Обратная совместимость со старой структурой
            baguette_id = data.get('baguette_id')
            if passepartouts:
                first_pp = passepartouts[0]
                passepartout_id = first_pp.get('passepartout_id')
                passepartout_length = first_pp.get('passepartout_length')
                passepartout_width = first_pp.get('passepartout_width')
            else:
                passepartout_id = data.get('passepartout_id')
                passepartout_length = data.get('passepartout_length')
                passepartout_width = data.get('passepartout_width')
        
        # x1, x2 для Order — из первой рамы или глобально
        ord_x1 = data.get('x1')
        ord_x2 = data.get('x2')
        if frames and frames[0].get('x1') and frames[0].get('x2'):
            ord_x1 = ord_x1 or frames[0].get('x1')
            ord_x2 = ord_x2 or frames[0].get('x2')
        order_data = {
            'x1': Decimal(str(ord_x1 or 0)),
            'x2': Decimal(str(ord_x2 or 0)),
            'baguette_id': baguette_id,
            'glass_id': data.get('glass_id'),
            # В Order сохраняется первая подкладка (FK), полный список — в frames_data
            'backing_id': backing_ids[0] if backing_ids else None,
        }
        
        # Подрамник опционально
        if data.get('podramnik_id'):
            order_data['podramnik_id'] = data.get('podramnik_id')
        
        # Паспарту опционально
        if passepartout_id:
            order_data['passepartout_id'] = passepartout_id
            if passepartout_length:
                order_data['passepartout_length'] = Decimal(str(passepartout_length))
            if passepartout_width:
                order_data['passepartout_width'] = Decimal(str(passepartout_width))
        
        # Фурнитура опциональна
        if data.get('hardware_id'):
            order_data['hardware_id'] = data.get('hardware_id')
            order_data['hardware_quantity'] = data.get('hardware_quantity', 1)
        
        # Упаковка опциональна; количество упаковки привязано к её выбору
        if data.get('package_id'):
            order_data['package_id'] = data.get('package_id')
            order_data['package_quantity'] = int(data.get('package_quantity', 1) or 1)
        else:
            order_data['package_quantity'] = 1

        # Натяжка опциональна
        if data.get('stretch_id'):
            order_data['stretch_id'] = data.get('stretch_id')

        # Опциональные компоненты
        if data.get('molding_id'):
            order_data['molding_id'] = data.get('molding_id')
            if data.get('molding_consumption'):
                order_data['molding_consumption'] = Decimal(str(data.get('molding_consumption')))
        
        if data.get('trosik_id'):
            order_data['trosik_id'] = data.get('trosik_id')
            if data.get('trosik_length'):
                order_data['trosik_length'] = PriceCalculator.normalize_length_to_meters(
                    Decimal(str(data.get('trosik_length')))
                )
        
        if data.get('podveski_id'):
            order_data['podveski_id'] = data.get('podveski_id')
            order_data['podveski_quantity'] = data.get('podveski_quantity')
        
        # Рассчитываем цену с учетом всех рамок
        if frames and len(frames) > 0:
            # Используем ту же логику, что и в calculate_price_api
            result = {
                'components': {},
                'total_price': Decimal('0')
            }
            
            x1 = order_data['x1']
            x2 = order_data['x2']
            frame_sizes = []
            for idx, frame in enumerate(frames):
                if frame.get('baguette_id'):
                    fx1 = Decimal(str(frame.get('x1', x1))) if frame.get('x1') else x1
                    fx2 = Decimal(str(frame.get('x2', x2))) if frame.get('x2') else x2
                    if not fx1 or not fx2 or fx1 <= 0 or fx2 <= 0:
                        fx1, fx2 = x1, x2
                    frame_sizes.append((fx1, fx2))
                    frame_calculation = PriceCalculator.calculate_total_price(
                        x1=fx1,
                        x2=fx2,
                        baguette_id=frame.get('baguette_id'),
                        work_id=frame.get('work_id'),
                    )
                    frame_num = idx + 1
                    for key, value in frame_calculation.get('components', {}).items():
                        if key in ['baguette', 'passepartout', 'work']:
                            result['total_price'] += Decimal(str(value.get('total_price', 0)))
                            result['components'][f'{key}_frame{frame_num}'] = {
                                **value,
                                'name': f"{value.get('name', key)} (Рама {frame_num})"
                            }
            for pp_data in passepartouts:
                pp_id = pp_data.get('passepartout_id')
                if not pp_id:
                    continue
                passepartout = Passepartout.objects.get(pk=pp_id)
                pp_length = Decimal(str(pp_data.get('passepartout_length'))) if pp_data.get('passepartout_length') else x1
                pp_width = Decimal(str(pp_data.get('passepartout_width'))) if pp_data.get('passepartout_width') else x2
                pp_area = PriceCalculator.calculate_glass_area(pp_length, pp_width)
                result['total_price'] += pp_area * passepartout.price
            if not frame_sizes:
                frame_sizes = [(x1, x2)]
            eff_x1, eff_x2 = frame_sizes[0]
            total_glass_area = sum(PriceCalculator.calculate_glass_area(fx1, fx2) for fx1, fx2 in frame_sizes)
            # Подкладка/подрамник — «на картину», считаются один раз по раме меньшего размера
            pic_x1, pic_x2 = min(frame_sizes, key=lambda s: s[0] * s[1])
            pic_area = PriceCalculator.calculate_glass_area(pic_x1, pic_x2)
            other_calculation = PriceCalculator.calculate_total_price(
                x1=eff_x1,
                x2=eff_x2,
                glass_id=None,
                backing_id=None,
                hardware_id=order_data.get('hardware_id'),
                hardware_quantity=order_data.get('hardware_quantity', 1),
                podramnik_id=order_data.get('podramnik_id'),
                package_id=order_data.get('package_id'),
                package_quantity=order_data.get('package_quantity', 1),
                molding_id=order_data.get('molding_id'),
                molding_consumption=order_data.get('molding_consumption'),
                trosik_id=order_data.get('trosik_id'),
                trosik_length=order_data.get('trosik_length'),
                podveski_id=order_data.get('podveski_id'),
                podveski_quantity=order_data.get('podveski_quantity'),
            )
            for key, value in other_calculation.get('components', {}).items():
                if key not in ('glass', 'stretch', 'backing', 'podramnik'):
                    result['total_price'] += Decimal(str(value.get('total_price', 0)))

            if backing_ids and pic_area > 0:
                _b_comps, _b_total = PriceCalculator.price_backings(backing_ids, pic_area)
                result['total_price'] += _b_total

            if order_data.get('podramnik_id'):
                podramnik = Podramnik.objects.get(pk=order_data['podramnik_id'])
                podramnik_qty = PriceCalculator.calculate_baguette_quantity(pic_x1, pic_x2, Decimal('0'))
                result['total_price'] += podramnik_qty * podramnik.price
            if order_data.get('glass_id') and total_glass_area > 0:
                from frames.models import Glass
                glass = Glass.objects.get(pk=order_data['glass_id'])
                gp = _floor(total_glass_area * glass.price_per_sqm, MIN_GLASS_PRICE)
                result['total_price'] += gp
            # Натяжка — работа мастера по периметру, учитывается в OrderExtrasCalculator ниже.

            calculation = result
        else:
            # Обратная совместимость: расчет для одной рамы
            calculation = PriceCalculator.calculate_total_price(
                x1=order_data['x1'],
                x2=order_data['x2'],
                baguette_id=order_data.get('baguette_id'),
                glass_id=order_data.get('glass_id'),
                backing_id=order_data.get('backing_id'),
                backing_ids=backing_ids,
                hardware_id=order_data.get('hardware_id'),
                hardware_quantity=order_data.get('hardware_quantity', 1),
                podramnik_id=order_data.get('podramnik_id'),
                package_id=order_data.get('package_id'),
                package_quantity=order_data.get('package_quantity', 1),
                molding_id=order_data.get('molding_id'),
                molding_consumption=order_data.get('molding_consumption'),
                trosik_id=order_data.get('trosik_id'),
                trosik_length=order_data.get('trosik_length'),
                podveski_id=order_data.get('podveski_id'),
                podveski_quantity=order_data.get('podveski_quantity'),
                passepartout_id=order_data.get('passepartout_id'),
                passepartout_length=order_data.get('passepartout_length'),
                passepartout_width=order_data.get('passepartout_width'),
                work_id=order_data.get('work_id'),
            )
        
        # Ручная сложность (доп. сумма) — сохраняем на заказе
        if data.get('manual_complexity'):
            order_data['manual_complexity'] = Decimal(str(data.get('manual_complexity')))

        # Работы (в цену) + ручная сложность
        extras = OrderExtrasCalculator.compute(
            frames=frames, passepartouts=passepartouts,
            x1=order_data['x1'], x2=order_data['x2'], data=data
        )
        order_quantity = int(data.get('quantity') or 1) or 1
        order_data['quantity'] = order_quantity
        OrderExtrasCalculator.apply(calculation, extras, quantity=order_quantity)

        order_data['total_price'] = Decimal(str(calculation['total_price']))
        order_data['status'] = 'new'
        
        # Данные клиента
        if data.get('customer_name'):
            order_data['customer_name'] = data.get('customer_name')
        if data.get('customer_phone'):
            order_data['customer_phone'] = data.get('customer_phone')
        if data.get('comment'):
            order_data['comment'] = data.get('comment').strip()
        if data.get('payment_method'):
            order_data['payment_method'] = data.get('payment_method')
        if data.get('advance_payment'):
            order_data['advance_payment'] = Decimal(str(data.get('advance_payment')))
            # Автоматически рассчитываем долг
            order_data['debt'] = order_data['total_price'] - order_data['advance_payment']
        else:
            order_data['advance_payment'] = Decimal('0')
            order_data['debt'] = order_data['total_price']
        
        # Сохраняем все рамы в JSON
        if frames and len(frames) > 0:
            frames_to_save = [dict(frame) for frame in frames]
            if passepartouts:
                frames_to_save[0]['passepartouts'] = passepartouts
            if backing_ids:
                frames_to_save[0]['backings'] = backing_ids
            order_data['frames_data'] = json.dumps(frames_to_save)

        # Создаем заказ
        order = Order.objects.create(**order_data)

        # Списание материалов со склада
        deduct_data = dict(order_data)
        deduct_data['backing_ids'] = backing_ids
        if data.get('stretch_id'):
            deduct_data['stretch_id'] = data['stretch_id']
        try:
            StockDeduction.deduct_from_order(deduct_data, frames or [], passepartouts=passepartouts, quantity=order_quantity)
        except Exception as deduct_err:
            # Логируем, но не отменяем заказ — заказ уже создан
            import logging
            logging.getLogger(__name__).warning(
                'Ошибка списания со склада для заказа %s: %s', order.pk, deduct_err
            )
        
        return Response({
            'success': True,
            'order_id': order.pk,
            'order': {
                'id': order.pk,
                'total_price': float(order.total_price),
                'status': order.status,
            }
        })
    
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=400)


@api_view(['GET'])
def get_orders(request):
    """API для получения краткого списка всех заказов"""
    try:
        orders = Order.objects.all().order_by('-created_at')
        
        data = []
        for order in orders:
            order_data = {
                'id': order.pk,
                'x1': float(order.x1),
                'x2': float(order.x2),
                'total_price': float(order.total_price),
                'status': order.status,
                'status_display': order.get_status_display(),
                'created_at': order.created_at.strftime('%d.%m.%Y %H:%M'),
                'customer_name': order.customer_name,
                'customer_phone': order.customer_phone,
                'advance_payment': float(order.advance_payment) if order.advance_payment else 0,
                'debt': float(order.debt) if order.debt else 0,
            }
            data.append(order_data)
        
        return Response(data)
    
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
def get_order_detail(request, order_id):
    """API для получения детальной информации о заказе с расчетами"""
    try:
        order = Order.objects.get(pk=order_id)

        # Список подкладок из frames_data (несколько), иначе одна из заказа
        order_backing_ids = []
        if order.frames_data:
            try:
                _sf = json.loads(order.frames_data)
                if isinstance(_sf, list) and _sf and isinstance(_sf[0], dict):
                    _emb = _sf[0].get('backings')
                    if isinstance(_emb, list):
                        order_backing_ids = [(b.get('backing_id') if isinstance(b, dict) else b)
                                             for b in _emb if b]
            except (json.JSONDecodeError, TypeError):
                pass
        if not order_backing_ids and order.backing_id:
            order_backing_ids = [order.backing_id]

        # Пересчитываем цену для получения детализации
        calculation = PriceCalculator.calculate_total_price(
            x1=order.x1,
            x2=order.x2,
            baguette_id=order.baguette.id if order.baguette else None,
            glass_id=order.glass.id if order.glass else None,
            backing_id=order.backing.id if order.backing else None,
            backing_ids=order_backing_ids,
            hardware_id=order.hardware.id if order.hardware else None,
            hardware_quantity=order.hardware_quantity or 1,
            podramnik_id=order.podramnik.id if order.podramnik else None,
            package_id=order.package.id if order.package else None,
            package_quantity=order.package_quantity or 1,
            molding_id=order.molding.id if order.molding else None,
            molding_consumption=order.molding_consumption,
            trosik_id=order.trosik.id if order.trosik else None,
            trosik_length=order.trosik_length,
            podveski_id=order.podveski.id if order.podveski else None,
            podveski_quantity=order.podveski_quantity,
            passepartout_id=order.passepartout.id if order.passepartout else None,
            passepartout_length=order.passepartout_length,
            passepartout_width=order.passepartout_width,
        )
        
        # Формируем информацию о рамах
        frames = []
        passepartouts_data = []
        
        # Если есть сохраненные данные о всех рамах, восстанавливаем их
        if order.frames_data:
            try:
                saved_frames = json.loads(order.frames_data)
                if isinstance(saved_frames, list) and saved_frames:
                    embedded_pp = saved_frames[0].get('passepartouts') if isinstance(saved_frames[0], dict) else []
                    if isinstance(embedded_pp, list):
                        passepartouts_data = embedded_pp
                for frame_data in saved_frames:
                    frame = {}
                    
                    # Восстанавливаем багет
                    if frame_data.get('baguette_id'):
                        try:
                            baguette = Baguette.objects.get(pk=frame_data['baguette_id'])
                            frame['baguette'] = {
                                'id': baguette.id,
                                'name': baguette.name,
                                'width': float(baguette.width),
                                'price': float(baguette.price),
                                'image': baguette.image.url if (baguette.image and hasattr(baguette.image, 'url')) else None,
                            }
                        except Baguette.DoesNotExist:
                            pass
                    
                    # Восстанавливаем паспарту
                    if frame_data.get('passepartout_id'):
                        try:
                            passepartout = Passepartout.objects.get(pk=frame_data['passepartout_id'])
                            pp_image_url = None
                            if passepartout.image and hasattr(passepartout.image, 'url'):
                                pp_image_url = request.build_absolute_uri(passepartout.image.url)
                            frame['passepartout'] = {
                                'id': passepartout.id,
                                'name': passepartout.name,
                                'price': float(passepartout.price),
                                'image': pp_image_url,
                                'length': float(frame_data['passepartout_length']) if frame_data.get('passepartout_length') else None,
                                'width': float(frame_data['passepartout_width']) if frame_data.get('passepartout_width') else None,
                            }
                        except Passepartout.DoesNotExist:
                            pass

                    # Сохраняем собственные размеры рамы (для корректного расчёта каждой)
                    frame['x1'] = frame_data.get('x1') or float(order.x1)
                    frame['x2'] = frame_data.get('x2') or float(order.x2)

                    if frame.get('baguette') or frame.get('passepartout'):
                        frames.append(frame)
            except (json.JSONDecodeError, KeyError) as e:
                # Если не удалось распарсить, используем старую логику
                pass
        
        # Если не удалось восстановить рамы из frames_data, используем старую логику (одна рама)
        if not frames and order.baguette:
            frame_from_order = {
                'x1': float(order.x1),
                'x2': float(order.x2),
                'baguette': {
                    'id': order.baguette.id,
                    'name': order.baguette.name,
                    'width': float(order.baguette.width),
                    'price': float(order.baguette.price),
                    'image': order.baguette.image.url if (order.baguette.image and hasattr(order.baguette.image, 'url')) else None,
                },
                'passepartout': {
                    'id': order.passepartout.id,
                    'name': order.passepartout.name,
                    'price': float(order.passepartout.price),
                    'image': request.build_absolute_uri(order.passepartout.image.url) if (order.passepartout.image and hasattr(order.passepartout.image, 'url')) else None,
                    'length': float(order.passepartout_length) if order.passepartout_length else None,
                    'width': float(order.passepartout_width) if order.passepartout_width else None,
                } if order.passepartout else None,
            }
            frames.append(frame_from_order)

        restored_passepartouts = []
        for pp in passepartouts_data:
            pp_id = pp.get('passepartout_id')
            if not pp_id:
                continue
            try:
                pp_obj = Passepartout.objects.get(pk=pp_id)
            except Passepartout.DoesNotExist:
                continue
            pp_image_url = None
            if pp_obj.image and hasattr(pp_obj.image, 'url'):
                pp_image_url = request.build_absolute_uri(pp_obj.image.url)
            restored_passepartouts.append({
                'id': pp_obj.id,
                'name': pp_obj.name,
                'price': float(pp_obj.price),
                'image': pp_image_url,
                'length': float(pp.get('passepartout_length')) if pp.get('passepartout_length') else None,
                'width': float(pp.get('passepartout_width')) if pp.get('passepartout_width') else None,
            })
        
        # Пересчитываем цену с учетом всех рамок
        if frames and len(frames) > 0:
            # Используем ту же логику, что и в calculate_price_api
            result = {
                'components': {},
                'total_price': Decimal('0')
            }
            
            # Рассчитываем цену для каждой рамы — по её собственному размеру
            for idx, frame in enumerate(frames):
                if frame.get('baguette') and frame['baguette'].get('id'):
                    f_x1 = Decimal(str(frame.get('x1') or order.x1))
                    f_x2 = Decimal(str(frame.get('x2') or order.x2))
                    frame_calculation = PriceCalculator.calculate_total_price(
                        x1=f_x1,
                        x2=f_x2,
                        baguette_id=frame['baguette']['id'],
                        passepartout_id=frame.get('passepartout', {}).get('id'),
                        passepartout_length=Decimal(str(frame.get('passepartout', {}).get('length'))) if frame.get('passepartout', {}).get('length') else None,
                        passepartout_width=Decimal(str(frame.get('passepartout', {}).get('width'))) if frame.get('passepartout', {}).get('width') else None,
                        work_id=frame.get('work_id'),
                    )
                    
                    # Добавляем компоненты рамы с префиксом номера (багет, паспарту, работа)
                    frame_num = idx + 1
                    for key, value in frame_calculation.get('components', {}).items():
                        if key in ['baguette', 'passepartout', 'work']:
                            component_key = f'{key}_frame{frame_num}'
                            result['components'][component_key] = {
                                **value,
                                'name': f"{value.get('name', key)} (Рама {frame_num})"
                            }
                            result['total_price'] += Decimal(str(value.get('total_price', 0)))

            for pp_idx, pp_data in enumerate(restored_passepartouts):
                pp_obj = Passepartout.objects.get(pk=pp_data['id'])
                pp_length = Decimal(str(pp_data.get('length'))) if pp_data.get('length') else order.x1
                pp_width = Decimal(str(pp_data.get('width'))) if pp_data.get('width') else order.x2
                pp_area = PriceCalculator.calculate_glass_area(pp_length, pp_width)
                pp_price = pp_area * pp_obj.price
                result['components'][f'passepartout_{pp_idx + 1}'] = {
                    'name': f"{pp_obj.name} (Паспарту {pp_idx + 1})",
                    'length': float(pp_length),
                    'width': float(pp_width),
                    'area': float(pp_area),
                    'unit_price': float(pp_obj.price),
                    'total_price': float(pp_price),
                }
                result['total_price'] += pp_price
            
            # Добавляем остальные компоненты (стекло, подкладка и т.д.) только один раз (работа привязана к раме)
            other_calculation = PriceCalculator.calculate_total_price(
                x1=order.x1,
                x2=order.x2,
                glass_id=order.glass.id if order.glass else None,
                backing_id=order.backing.id if order.backing else None,
                backing_ids=order_backing_ids,
                hardware_id=order.hardware.id if order.hardware else None,
                hardware_quantity=order.hardware_quantity or 1,
                podramnik_id=order.podramnik.id if order.podramnik else None,
                package_id=order.package.id if order.package else None,
                package_quantity=order.package_quantity or 1,
                molding_id=order.molding.id if order.molding else None,
                molding_consumption=order.molding_consumption,
                trosik_id=order.trosik.id if order.trosik else None,
                trosik_length=order.trosik_length,
                podveski_id=order.podveski.id if order.podveski else None,
                podveski_quantity=order.podveski_quantity,
                stretch_id=order.stretch.id if order.stretch else None,
            )

            # Добавляем остальные компоненты
            for key, value in other_calculation.get('components', {}).items():
                result['components'][key] = value
                result['total_price'] += Decimal(str(value.get('total_price', 0)))

            calculation = result
        else:
            # Обратная совместимость: расчет для одной рамы
            calculation = PriceCalculator.calculate_total_price(
                x1=order.x1,
                x2=order.x2,
                baguette_id=order.baguette.id if order.baguette else None,
                glass_id=order.glass.id if order.glass else None,
                backing_id=order.backing.id if order.backing else None,
                backing_ids=order_backing_ids,
                hardware_id=order.hardware.id if order.hardware else None,
                hardware_quantity=order.hardware_quantity or 1,
                podramnik_id=order.podramnik.id if order.podramnik else None,
                package_id=order.package.id if order.package else None,
                package_quantity=order.package_quantity or 1,
                molding_id=order.molding.id if order.molding else None,
                molding_consumption=order.molding_consumption,
                trosik_id=order.trosik.id if order.trosik else None,
                trosik_length=order.trosik_length,
                podveski_id=order.podveski.id if order.podveski else None,
                podveski_quantity=order.podveski_quantity,
                passepartout_id=order.passepartout.id if order.passepartout else None,
                passepartout_length=order.passepartout_length,
                passepartout_width=order.passepartout_width,
                stretch_id=order.stretch.id if order.stretch else None,
            )

        # Работы + сложность — пересчёт для детализации.
        # Рамы берём из сырого frames_data (включая рамы без багета).
        extras_frames = []
        if order.frames_data:
            try:
                for f in json.loads(order.frames_data):
                    if isinstance(f, dict):
                        extras_frames.append({
                            'baguette_id': f.get('baguette_id'),
                            'x1': f.get('x1') or order.x1,
                            'x2': f.get('x2') or order.x2,
                        })
            except (json.JSONDecodeError, TypeError):
                pass
        if not extras_frames and order.baguette_id:
            extras_frames = [{'baguette_id': order.baguette_id, 'x1': order.x1, 'x2': order.x2}]
        extras_pps = [{'passepartout_id': p['id']} for p in restored_passepartouts]
        for fr in frames:
            pp = fr.get('passepartout')
            if pp and pp.get('id'):
                extras_pps.append({'passepartout_id': pp['id']})
        extras_data = {
            'baguette_id': order.baguette_id,
            'glass_id': order.glass_id,
            'backing_id': order.backing_id,
            'backing_ids': order_backing_ids,
            'hardware_id': order.hardware_id,
            'hardware_quantity': order.hardware_quantity,
            'podramnik_id': order.podramnik_id,
            'molding_id': order.molding_id,
            'package_id': order.package_id,
            'stretch_id': order.stretch_id,
            'manual_complexity': order.manual_complexity,
            'quantity': 1,
        }
        extras = OrderExtrasCalculator.compute(
            frames=extras_frames, passepartouts=extras_pps,
            x1=order.x1, x2=order.x2, data=extras_data,
        )
        OrderExtrasCalculator.apply(calculation, extras, quantity=order.quantity)

        order_data = {
            'id': order.pk,
            'x1': float(order.x1),
            'x2': float(order.x2),
            'frames': frames,
            'passepartouts': restored_passepartouts,
            'glass': {
                'id': order.glass.id,
                'name': order.glass.name,
                'price_per_sqm': float(order.glass.price_per_sqm),
            } if order.glass else None,
            'backing': {
                'id': order.backing.id,
                'name': order.backing.name,
                'price': float(order.backing.price),
            } if order.backing else None,
            'backings': [
                {'id': _bk.id, 'name': _bk.name, 'price': float(_bk.price)}
                for _bk in (Backing.objects.filter(pk=_bid).first() for _bid in order_backing_ids)
                if _bk
            ],
            'stretch': {
                'id': order.stretch.id,
                'name': order.stretch.name,
                'price_per_meter': float(order.stretch.price_per_meter),
            } if order.stretch else None,
            'podramnik': {
                'id': order.podramnik.id,
                'name': order.podramnik.name,
                'price': float(order.podramnik.price),
            } if order.podramnik else None,
            'hardware': {
                'id': order.hardware.id,
                'name': order.hardware.name,
                'price_per_unit': float(order.hardware.price_per_unit),
                'quantity': order.hardware_quantity,
            } if order.hardware else None,
            'package': {
                'id': order.package.id,
                'name': order.package.name,
                'price': float(order.package.price),
            } if order.package else None,
            'package_quantity': order.package_quantity or 1,
            'quantity': order.quantity or 1,
            'molding': {
                'id': order.molding.id,
                'name': order.molding.name,
                'price_per_meter': float(order.molding.price_per_meter),
                'consumption': float(order.molding_consumption) if order.molding_consumption else None,
            } if order.molding else None,
            'trosik': {
                'id': order.trosik.id,
                'name': order.trosik.name,
                'price_per_meter': float(order.trosik.price_per_meter),
                'length': float(order.trosik_length) if order.trosik_length else None,
            } if order.trosik else None,
            'podveski': {
                'id': order.podveski.id,
                'name': order.podveski.name,
                'price_per_unit': float(order.podveski.price_per_unit),
                'quantity': order.podveski_quantity,
            } if order.podveski else None,
            'total_price': float(order.total_price),
            'status': order.status,
            'status_display': order.get_status_display(),
            'created_at': order.created_at.strftime('%d.%m.%Y %H:%M'),
            'updated_at': order.updated_at.strftime('%d.%m.%Y %H:%M') if order.updated_at else None,
            'calculation': calculation,  # Детализация расчетов
            # Данные клиента
            'customer_name': order.customer_name,
            'customer_phone': order.customer_phone,
            'payment_method': order.payment_method,
            'advance_payment': float(order.advance_payment) if order.advance_payment else 0,
            'debt': float(order.debt) if order.debt else 0,
            'manual_complexity': float(order.manual_complexity) if order.manual_complexity else 0,
        }

        return Response(order_data)
    
    except Order.DoesNotExist:
        return Response({'error': 'Заказ не найден'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['PATCH'])
def update_order_status(request, order_id):
    """API для изменения статуса заказа"""
    try:
        order = Order.objects.get(pk=order_id)
        data = request.data

        new_status = data.get('status')
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({'error': 'Некорректный статус'}, status=400)
        
        order.status = new_status
        order.save()
        
        return Response({
            'success': True,
            'order_id': order.pk,
            'status': order.status,
            'status_display': order.get_status_display(),
        })
    
    except Order.DoesNotExist:
        return Response({'error': 'Заказ не найден'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
def generate_receipt(request, order_id):
    """API для генерации Word документа квитанции"""
    try:
        from orders.receipt_generator import generate_receipt_word
        doc_io = generate_receipt_word(order_id)
        
        response = HttpResponse(
            doc_io.read(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="receipt_{order_id}.docx"'
        
        return response
    
    except ValueError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"ValueError при генерации квитанции для заказа {order_id}: {str(e)}")
        return Response({'error': str(e)}, status=404)
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        error_traceback = traceback.format_exc()
        logger.error(f"Ошибка при генерации квитанции для заказа {order_id}: {str(e)}\n{error_traceback}")
        return Response({'error': str(e), 'traceback': error_traceback}, status=400)


@api_view(['GET'])
def receipt_print(request, order_id):
    """HTML-квитанция для печати (открывается в новом окне с автопечатью)"""
    try:
        from orders.receipt_generator import generate_receipt_html
        html_content = generate_receipt_html(order_id)
        return HttpResponse(html_content, content_type='text/html; charset=utf-8')
    except ValueError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"ValueError при генерации HTML квитанции для заказа {order_id}: {str(e)}")
        return Response({'error': str(e)}, status=404)
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        error_traceback = traceback.format_exc()
        logger.error(f"Ошибка при генерации HTML квитанции для заказа {order_id}: {str(e)}\n{error_traceback}")
        return Response({'error': str(e), 'traceback': error_traceback}, status=400)
