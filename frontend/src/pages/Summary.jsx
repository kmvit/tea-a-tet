import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useOrder } from '../context/OrderContext';
import { createOrder } from '../api';
import { ProgressBar } from '../components/ProgressBar';
import { WorksPanel } from '../components/WorksPanel';

export const Summary = () => {
  const navigate = useNavigate();
  const { orderData, priceCalculation, updateOrderData, resetOrder, calculateCurrentPrice } = useOrder();
  const [loading, setLoading] = useState(false);
  const [orderCreated, setOrderCreated] = useState(false);
  const [orderId, setOrderId] = useState(null);

  // Пересчёт при изменении ручной сложности или количества копий
  useEffect(() => {
    calculateCurrentPrice();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orderData.manual_complexity, orderData.quantity]);

  const handleCreateOrder = async () => {
    setLoading(true);
    try {
      const dataToSend = {
        x1: orderData.x1,
        x2: orderData.x2,
        glass_id: orderData.glass_id,
        backing_id: orderData.backing_id,
        stretch_id: orderData.stretch_id,
        hardware_id: orderData.hardware_id,
        hardware_quantity: orderData.hardware_quantity,
        podramnik_id: orderData.podramnik_id,
        package_id: orderData.package_id,
        package_quantity: orderData.package_quantity,
        molding_id: orderData.molding_id,
        molding_consumption: orderData.molding_consumption,
        trosik_id: orderData.trosik_id,
        trosik_length: orderData.trosik_length,
        podveski_id: orderData.podveski_id,
        podveski_quantity: orderData.podveski_quantity,
        customer_name: orderData.customer_name,
        customer_phone: orderData.customer_phone,
        payment_method: orderData.payment_method || 'наличные',
        advance_payment: orderData.advance_payment,
        comment: orderData.comment || null,
        manual_complexity: orderData.manual_complexity || 0,
        quantity: orderData.quantity || 1,
      };

      if (orderData.frames && orderData.frames.length > 0) {
        dataToSend.frames = orderData.frames.map(frame => ({
          baguette_id: frame.baguette_id,
          x1: frame.x1,
          x2: frame.x2,
        }));
        dataToSend.passepartouts = orderData.passepartouts || [];
      } else {
        if (orderData.baguette_id) {
          dataToSend.baguette_id = orderData.baguette_id;
          dataToSend.passepartout_id = orderData.passepartout_id;
          dataToSend.passepartout_length = orderData.passepartout_length;
          dataToSend.passepartout_width = orderData.passepartout_width;
        }
      }

      const response = await createOrder(dataToSend);
      const newOrderId = response.data.order_id;
      setOrderId(newOrderId);
      setOrderCreated(true);
      resetOrder();

      // Открываем квитанцию (та же, что в кабинете) сразу в окне печати
      window.open(`/api/orders/${newOrderId}/receipt/print/`, '_blank', 'width=800,height=900');
    } catch (error) {
      console.error('Ошибка создания заказа:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Неизвестная ошибка';
      alert(`Ошибка создания заказа: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  if (orderCreated) {
    return (
      <div className="bg-gradient-to-br from-gray-50 to-gray-100 py-8">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-xl p-8 text-center">
            <div className="text-6xl mb-4">✅</div>
            <h2 className="text-3xl font-bold text-gray-800 mb-4">
              Заказ успешно создан!
            </h2>
            <p className="text-gray-600 mb-6">
              Номер заказа: <strong>#{orderId}</strong>
            </p>
            <p className="text-sm text-gray-500 mb-6">
              Квитанция открыта в новом окне для печати
            </p>
            <button
              onClick={() => navigate('/')}
              className="bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition"
            >
              Создать новый заказ
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-gray-50 to-gray-100 py-8">
      <div className="container mx-auto px-4">
        <ProgressBar />

        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-3xl font-bold text-gray-800 mb-6">
              Итоговая сводка заказа
            </h2>

            <div className="space-y-6 mb-8">
              <div>
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  Размеры
                </h3>
                {orderData.frames && orderData.frames.length > 1 ? (
                  <div className="space-y-1">
                    {orderData.frames.map(
                      (frame, i) =>
                        frame.baguette_id &&
                        (frame.x1 || frame.x2) && (
                          <p key={i} className="text-gray-600">
                            Рама {i + 1}: {frame.x1} × {frame.x2} см
                          </p>
                        )
                    )}
                  </div>
                ) : (
                  <p className="text-gray-600">
                    X1: {orderData.x1} см × X2: {orderData.x2} см
                  </p>
                )}
              </div>

              {priceCalculation && priceCalculation.components && (
                <div>
                  <h3 className="text-xl font-semibold text-gray-700 mb-4">
                    Материалы
                  </h3>
                  <div className="space-y-2">
                    {Object.entries(priceCalculation.components).map(
                      ([key, component]) => (
                        <div
                          key={key}
                          className="flex justify-between py-2 border-b border-gray-200"
                        >
                          <span className="text-gray-600">{component.name}</span>
                          <span className="font-medium">
                            {component.total_price.toFixed(2)} ₽
                          </span>
                        </div>
                      )
                    )}
                  </div>
                  <div className="flex justify-between mt-2 pt-2 border-t border-gray-300 font-semibold text-gray-800">
                    <span>Итого материалов</span>
                    <span className="tabular-nums">
                      {Object.values(priceCalculation.components)
                        .reduce((s, c) => s + (c.total_price || 0), 0)
                        .toFixed(2)}{' '}
                      ₽
                    </span>
                  </div>
                </div>
              )}

              {priceCalculation?.works && (
                <WorksPanel works={priceCalculation.works} />
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Количество копий
                </label>
                <input
                  type="number"
                  min="1"
                  step="1"
                  value={orderData.quantity ?? 1}
                  onChange={(e) => {
                    const v = parseInt(e.target.value) || 1;
                    updateOrderData({ quantity: v < 1 ? 1 : v });
                  }}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                  placeholder="1"
                />
                <p className="text-xs text-gray-500 mt-1">Заказ на N одинаковых изделий — вся стоимость умножается на количество</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Сложность (доп. сумма, ₽)
                </label>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={orderData.manual_complexity ?? ''}
                  onChange={(e) => {
                    const v = e.target.value;
                    updateOrderData({ manual_complexity: v === '' ? null : parseFloat(v) });
                  }}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                  placeholder="0"
                />
                <p className="text-xs text-gray-500 mt-1">Добавляется к итоговой стоимости полностью</p>
              </div>

              <div className="border-t-2 border-gray-300 pt-4">
                <div className="flex justify-between items-center">
                  <span className="text-2xl font-bold text-gray-800">Итого:</span>
                  <span className="text-3xl font-bold text-blue-600">
                    {priceCalculation?.total_price
                      ? `${priceCalculation.total_price.toFixed(2)} ₽`
                      : '0 ₽'}
                  </span>
                </div>
              </div>
            </div>

            {orderData.customer_name && (
              <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-700 mb-2">
                  Данные клиента
                </h3>
                <div className="space-y-1 text-gray-600">
                  <p><strong>Имя:</strong> {orderData.customer_name}</p>
                  <p><strong>Телефон:</strong> {orderData.customer_phone}</p>
                  <p><strong>Способ оплаты:</strong> {orderData.payment_method || 'наличные'}</p>
                  {orderData.advance_payment && (
                    <p><strong>Аванс:</strong> {parseFloat(orderData.advance_payment).toFixed(2)} ₽</p>
                  )}
                </div>
              </div>
            )}

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Комментарий к заказу
              </label>
              <textarea
                value={orderData.comment || ''}
                onChange={(e) => updateOrderData({ comment: e.target.value })}
                rows={3}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition resize-y"
                placeholder="Введите комментарий к заказу (опционально)"
              />
            </div>

            <div className="flex space-x-4">
              <button
                onClick={() => navigate('/')}
                className="flex-1 bg-gray-200 text-gray-800 py-3 px-6 rounded-lg font-semibold hover:bg-gray-300 transition"
              >
                Назад
              </button>
              <button
                onClick={handleCreateOrder}
                disabled={loading}
                className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {loading ? 'Создание заказа...' : 'Создать заказ'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
