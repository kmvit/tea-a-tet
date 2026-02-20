from django.urls import path
from . import api_views

app_name = 'frames'

urlpatterns = [
    path('api/baguettes/', api_views.get_baguettes, name='api_baguettes'),
    path('api/glasses/', api_views.get_glasses, name='api_glasses'),
    path('api/backings/', api_views.get_backings, name='api_backings'),
    path('api/hardware/', api_views.get_hardware, name='api_hardware'),
    path('api/podramniki/', api_views.get_podramniki, name='api_podramniki'),
    path('api/packages/', api_views.get_packages, name='api_packages'),
    path('api/moldings/', api_views.get_moldings, name='api_moldings'),
    path('api/trosiki/', api_views.get_trosiki, name='api_trosiki'),
    path('api/podveski/', api_views.get_podveski, name='api_podveski'),
    path('api/passepartout/', api_views.get_passepartout, name='api_passepartout'),
    path('api/stretches/', api_views.get_stretches, name='api_stretches'),
    path('api/works/', api_views.get_works, name='api_works'),
    path('api/calculate-price/', api_views.calculate_price_api, name='api_calculate_price'),
    path('api/create-order/', api_views.create_order_api, name='api_create_order'),
    path('api/orders/', api_views.get_orders, name='api_orders'),
    path('api/orders/<int:order_id>/', api_views.get_order_detail, name='api_order_detail'),
    path('api/orders/<int:order_id>/status/', api_views.update_order_status, name='api_update_order_status'),
    path('api/orders/<int:order_id>/receipt/', api_views.generate_receipt, name='api_generate_receipt'),
    path('api/orders/<int:order_id>/receipt/print/', api_views.receipt_print, name='api_receipt_print'),
]
