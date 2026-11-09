from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from orders.models import Order
from orders.receipt_generator import generate_receipt_html
from .services import OrderExtrasCalculator


class OrderWorkflowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.payload = {
            'x1': 40, 'x2': 40, 'mount_count': 3, 'quantity': 2,
            'customer_name': 'Тест', 'customer_phone': '+79990000000',
            'advance_payment': 150, 'manual_complexity': 200,
        }

    def test_mount_is_entirely_carpenter_work_and_survives_save(self):
        calculated = self.client.post('/api/calculate-price/', self.payload, format='json')
        self.assertEqual(calculated.status_code, 200)
        self.assertEqual(calculated.data['total_price'], 1000)
        mount = next(w for w in calculated.data['works']['items'] if w['operation_type'] == 'object_mount')
        self.assertEqual(mount['total'], 600)
        self.assertEqual(calculated.data['works']['total_rate'], 800)
        response = self.client.post('/api/create-order/', self.payload, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        order = Order.objects.get(pk=response.data['order_id'])
        self.assertEqual(order.mount_count, 3)
        self.assertEqual(order.total_price, Decimal('1000'))
        self.assertEqual(order.advance_payment, Decimal('150'))
        self.assertEqual(order.debt, Decimal('850'))
        detail = self.client.get(f'/api/orders/{order.pk}/')
        self.assertEqual(detail.status_code, 200, detail.data)
        self.assertEqual(detail.data['mount_count'], 3)
        self.assertEqual(detail.data['calculation']['total_price'], 1000)
        html = generate_receipt_html(order.pk)
        self.assertIn('Крепление предметов (3 шт × 100 ₽)', html)
        self.assertIn('600 руб', html)
        self.assertIn('850 руб', html)
        self.assertLess(html.index('<div class="order-tag">'), html.index('Пункты заказа:'))

    def test_advance_must_be_explicit_but_zero_is_valid(self):
        for invalid in (None, '', -1, 'NaN', 'Infinity', '1.001'):
            with self.subTest(invalid=invalid):
                payload = {**self.payload, 'advance_payment': invalid}
                response = self.client.post('/api/create-order/', payload, format='json')
                self.assertEqual(response.status_code, 400)
        payload = dict(self.payload)
        payload.pop('advance_payment')
        self.assertEqual(self.client.post('/api/create-order/', payload, format='json').status_code, 400)
        self.assertEqual(Order.objects.count(), 0)
        response = self.client.post('/api/create-order/', {**payload, 'advance_payment': 0}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        order = Order.objects.get()
        self.assertEqual(order.advance_payment, 0)
        self.assertEqual(order.debt, order.total_price)

    def test_mount_quantity_validation(self):
        for invalid in (-1, 1.5, 'bad', 'NaN'):
            with self.subTest(invalid=invalid):
                response = self.client.post('/api/calculate-price/', {**self.payload, 'mount_count': invalid}, format='json')
                self.assertEqual(response.status_code, 400)
                response = self.client.post('/api/create-order/', {**self.payload, 'mount_count': invalid}, format='json')
                self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_existing_order_defaults_to_no_mount_work(self):
        order = Order.objects.create(x1=40, x2=40, total_price=0)
        extras = OrderExtrasCalculator.for_order(order)
        self.assertEqual(extras['works']['items'], [])
