import { useState, useEffect } from 'react';
import { getOrders, getOrderDetail, updateOrderStatus, generateReceipt } from '../api';

const STATUS_COLORS = {
  new: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-yellow-100 text-yellow-800',
  ready: 'bg-green-100 text-green-800',
  issued: 'bg-gray-100 text-gray-800',
};

const STATUS_LABELS = {
  new: 'Новый',
  in_progress: 'В работе',
  ready: 'Готов',
  issued: 'Выдан',
};

const STATUS_OPTIONS = [
  { value: 'new', label: 'Новый' },
  { value: 'in_progress', label: 'В работе' },
  { value: 'ready', label: 'Готов' },
  { value: 'issued', label: 'Выдан' },
];

export const Cabinet = () => {
  const [orders, setOrders] = useState([]);
  const [expandedOrders, setExpandedOrders] = useState(new Set());
  const [orderDetails, setOrderDetails] = useState({});
  const [loading, setLoading] = useState(true);
  const [loadingDetails, setLoadingDetails] = useState(new Set());
  const [error, setError] = useState(null);
  const [updatingStatus, setUpdatingStatus] = useState(new Set());
  const [generatingReceipt, setGeneratingReceipt] = useState(new Set());

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setLoading(true);
        const response = await getOrders();
        setOrders(response.data);
        setError(null);
      } catch (err) {
        console.error('Ошибка загрузки заказов:', err);
        setError('Не удалось загрузить заказы');
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  const handleToggleOrder = async (orderId) => {
    const newExpanded = new Set(expandedOrders);
    
    if (newExpanded.has(orderId)) {
      newExpanded.delete(orderId);
    } else {
      newExpanded.add(orderId);
      
      // Загружаем детали, если еще не загружены
      if (!orderDetails[orderId]) {
        setLoadingDetails(new Set([...loadingDetails, orderId]));
        try {
          const response = await getOrderDetail(orderId);
          setOrderDetails(prev => ({
            ...prev,
            [orderId]: response.data,
          }));
        } catch (err) {
          console.error('Ошибка загрузки деталей заказа:', err);
        } finally {
          setLoadingDetails(prev => {
            const newSet = new Set(prev);
            newSet.delete(orderId);
            return newSet;
          });
        }
      }
    }
    
    setExpandedOrders(newExpanded);
  };

  const handleStatusChange = async (orderId, newStatus) => {
    setUpdatingStatus(new Set([...updatingStatus, orderId]));
    try {
      await updateOrderStatus(orderId, newStatus);
      
      // Обновляем статус в списке заказов
      setOrders(prev => prev.map(order => 
        order.id === orderId 
          ? { ...order, status: newStatus, status_display: STATUS_LABELS[newStatus] }
          : order
      ));
      
      // Обновляем статус в деталях, если они загружены
      if (orderDetails[orderId]) {
        setOrderDetails(prev => ({
          ...prev,
          [orderId]: {
            ...prev[orderId],
            status: newStatus,
            status_display: STATUS_LABELS[newStatus],
          },
        }));
      }
    } catch (err) {
      console.error('Ошибка изменения статуса:', err);
      alert('Не удалось изменить статус заказа');
    } finally {
      setUpdatingStatus(prev => {
        const newSet = new Set(prev);
        newSet.delete(orderId);
        return newSet;
      });
    }
  };

  const handleGenerateReceipt = async (orderId) => {
    setGeneratingReceipt(new Set([...generatingReceipt, orderId]));
    try {
      await generateReceipt(orderId);
    } catch (err) {
      console.error('Ошибка генерации квитанции:', err);
      const errorMessage = err.message || 'Не удалось сгенерировать квитанцию';
      alert(`Ошибка генерации квитанции: ${errorMessage}`);
    } finally {
      setGeneratingReceipt(prev => {
        const newSet = new Set(prev);
        newSet.delete(orderId);
        return newSet;
      });
    }
  };

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-gray-50 to-gray-100 py-8">
        <div className="container mx-auto px-4">
          <div className="text-center py-20">
            <div className="text-xl text-gray-600">Загрузка заказов...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gradient-to-br from-gray-50 to-gray-100 py-8">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-xl p-8">
            <div className="text-center py-8">
              <div className="text-red-600 text-xl mb-4">{error}</div>
              <button
                onClick={() => window.location.reload()}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Обновить
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-gray-50 to-gray-100 py-8">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">Мой кабинет</h1>

          {orders.length === 0 ? (
            <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
              <div className="text-gray-400 text-6xl mb-4">📦</div>
              <h2 className="text-2xl font-semibold text-gray-700 mb-2">
                Заказов пока нет
              </h2>
              <p className="text-gray-600">
                Создайте свой первый заказ, чтобы он появился здесь
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {orders.map((order) => {
                const isExpanded = expandedOrders.has(order.id);
                const details = orderDetails[order.id];
                const isLoadingDetails = loadingDetails.has(order.id);
                const isUpdating = updatingStatus.has(order.id);

                return (
                  <div
                    key={order.id}
                    className="bg-white rounded-2xl shadow-xl overflow-hidden hover:shadow-2xl transition-shadow"
                  >
                    {/* Краткая информация о заказе */}
                    <div
                      className="p-6 cursor-pointer"
                      onClick={() => handleToggleOrder(order.id)}
                    >
                      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                        <div className="flex items-center space-x-4 mb-4 md:mb-0">
                          <div className="text-2xl">📋</div>
                          <div>
                            <h3 className="text-xl font-bold text-gray-800">
                              Заказ #{order.id}
                            </h3>
                            <p className="text-sm text-gray-500">
                              Создан: {order.created_at}
                            </p>
                            <p className="text-sm text-gray-600 mt-1">
                              Размер: {order.x1} см × {order.x2} см
                            </p>
                            {order.customer_name && (
                              <p className="text-sm text-gray-700 mt-1">
                                Клиент: <strong>{order.customer_name}</strong>
                                {order.customer_phone && ` (${order.customer_phone})`}
                              </p>
                            )}
                            {order.advance_payment > 0 && (
                              <p className="text-xs text-gray-500 mt-1">
                                Аванс: {order.advance_payment.toFixed(2)} ₽
                                {order.debt > 0 && ` | Долг: ${order.debt.toFixed(2)} ₽`}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <span
                            className={`px-4 py-2 rounded-full text-sm font-semibold ${
                              STATUS_COLORS[order.status] || STATUS_COLORS.new
                            }`}
                          >
                            {order.status_display || STATUS_LABELS[order.status] || 'Новый'}
                          </span>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-blue-600">
                              {order.total_price.toFixed(2)} ₽
                            </div>
                            {order.advance_payment > 0 && (
                              <div className="text-xs text-gray-500 mt-1">
                                Оплачено: {order.advance_payment.toFixed(2)} ₽
                              </div>
                            )}
                          </div>
                          <div className="text-gray-400">
                            {isExpanded ? '▼' : '▶'}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Детальная информация (раскрывается при клике) */}
                        {isExpanded && (
                      <div className="border-t border-gray-200 p-6 bg-gray-50">
                        {isLoadingDetails ? (
                          <div className="text-center py-8">
                            <div className="text-gray-600">Загрузка деталей...</div>
                          </div>
                        ) : details ? (
                          <div className="space-y-6">
                            {/* Действия с заказом */}
                            <div className="bg-white p-4 rounded-lg border-2 border-gray-200">
                              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                                <div className="flex-1">
                                  <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Статус заказа
                                  </label>
                                  <select
                                    value={details.status}
                                    onChange={(e) => handleStatusChange(order.id, e.target.value)}
                                    disabled={isUpdating}
                                    className="w-full md:w-auto px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition disabled:bg-gray-100 disabled:cursor-not-allowed"
                                  >
                                    {STATUS_OPTIONS.map(option => (
                                      <option key={option.value} value={option.value}>
                                        {option.label}
                                      </option>
                                    ))}
                                  </select>
                                  {isUpdating && (
                                    <span className="ml-2 text-sm text-gray-500">Обновление...</span>
                                  )}
                                </div>
                                <div>
                                  <button
                                    onClick={() => handleGenerateReceipt(order.id)}
                                    disabled={generatingReceipt.has(order.id)}
                                    className="px-6 py-2 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
                                  >
                                    {generatingReceipt.has(order.id) ? (
                                      <>
                                        <span className="animate-spin">⏳</span>
                                        <span>Генерация...</span>
                                      </>
                                    ) : (
                                      <>
                                        <span>📄</span>
                                        <span>Скачать квитанцию</span>
                                      </>
                                    )}
                                  </button>
                                </div>
                              </div>
                            </div>

                            {/* Рамы */}
                            {details.frames && details.frames.length > 0 && (
                              <div className="bg-white p-4 rounded-lg border-2 border-gray-200">
                                <h4 className="text-lg font-semibold text-gray-800 mb-4">
                                  Рамы ({details.frames.length})
                                </h4>
                                <div className="space-y-4">
                                  {details.frames.map((frame, idx) => (
                                    <div key={idx} className="bg-gray-50 p-4 rounded-lg">
                                      <h5 className="font-semibold text-gray-700 mb-3">
                                        Рама {idx + 1}
                                      </h5>
                                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {frame.baguette && (
                                          <div>
                                            <p className="text-sm text-gray-500 mb-1">Багет</p>
                                            <p className="font-medium text-gray-800">
                                              {frame.baguette.name}
                                            </p>
                                            <p className="text-xs text-gray-600">
                                              Ширина: {frame.baguette.width} см, Цена: {frame.baguette.price} ₽/м
                                            </p>
                                          </div>
                                        )}
                                        {frame.passepartout && (
                                          <div>
                                            <p className="text-sm text-gray-500 mb-1">Паспарту</p>
                                            <p className="font-medium text-gray-800">
                                              {frame.passepartout.name}
                                            </p>
                                            {frame.passepartout.length && frame.passepartout.width && (
                                              <p className="text-xs text-gray-600">
                                                Размер: {frame.passepartout.length}×{frame.passepartout.width} см
                                              </p>
                                            )}
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Остальные компоненты */}
                            <div className="bg-white p-4 rounded-lg border-2 border-gray-200">
                              <h4 className="text-lg font-semibold text-gray-800 mb-4">
                                Компоненты
                              </h4>
                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {details.glass && (
                                  <div>
                                    <p className="text-sm text-gray-500 mb-1">Стекло</p>
                                    <p className="font-medium text-gray-800">
                                      {details.glass.name}
                                    </p>
                                    <p className="text-xs text-gray-600">
                                      {details.glass.price_per_sqm} ₽/кв.м
                                    </p>
                                  </div>
                                )}
                                {details.backing && (
                                  <div>
                                    <p className="text-sm text-gray-500 mb-1">Подкладка</p>
                                    <p className="font-medium text-gray-800">
                                      {details.backing.name}
                                    </p>
                                    <p className="text-xs text-gray-600">
                                      {details.backing.price} ₽
                                    </p>
                                  </div>
                                )}
                                {details.podramnik && (
                                  <div>
                                    <p className="text-sm text-gray-500 mb-1">Подрамник</p>
                                    <p className="font-medium text-gray-800">
                                      {details.podramnik.name}
                                    </p>
                                    <p className="text-xs text-gray-600">
                                      {details.podramnik.price} ₽
                                    </p>
                                  </div>
                                )}
                                {details.hardware && (
                                  <div>
                                    <p className="text-sm text-gray-500 mb-1">Фурнитура</p>
                                    <p className="font-medium text-gray-800">
                                      {details.hardware.name}
                                    </p>
                                    <p className="text-xs text-gray-600">
                                      {details.hardware.price_per_unit} ₽/шт × {details.hardware.quantity}
                                    </p>
                                  </div>
                                )}
                                {details.package && (
                                  <div>
                                    <p className="text-sm text-gray-500 mb-1">Упаковка</p>
                                    <p className="font-medium text-gray-800">
                                      {details.package.name}
                                    </p>
                                    <p className="text-xs text-gray-600">
                                      {details.package.price} ₽
                                    </p>
                                  </div>
                                )}
                                {details.molding && (
                                  <div>
                                    <p className="text-sm text-gray-500 mb-1">Молдинг</p>
                                    <p className="font-medium text-gray-800">
                                      {details.molding.name}
                                    </p>
                                    {details.molding.consumption && (
                                      <p className="text-xs text-gray-600">
                                        {details.molding.price_per_meter} ₽/м × {details.molding.consumption} м
                                      </p>
                                    )}
                                  </div>
                                )}
                                {details.trosik && (
                                  <div>
                                    <p className="text-sm text-gray-500 mb-1">Тросик</p>
                                    <p className="font-medium text-gray-800">
                                      {details.trosik.name}
                                    </p>
                                    {details.trosik.length && (
                                      <p className="text-xs text-gray-600">
                                        {details.trosik.price_per_meter} ₽/м × {details.trosik.length} м
                                      </p>
                                    )}
                                  </div>
                                )}
                                {details.podveski && (
                                  <div>
                                    <p className="text-sm text-gray-500 mb-1">Подвески</p>
                                    <p className="font-medium text-gray-800">
                                      {details.podveski.name}
                                    </p>
                                    <p className="text-xs text-gray-600">
                                      {details.podveski.price_per_unit} ₽/шт × {details.podveski.quantity}
                                    </p>
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* Расчеты */}
                            {details.calculation && details.calculation.components && (
                              <div className="bg-white p-4 rounded-lg border-2 border-gray-200">
                                <h4 className="text-lg font-semibold text-gray-800 mb-4">
                                  Детализация расчетов
                                </h4>
                                <div className="space-y-2">
                                  {Object.entries(details.calculation.components).map(
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
                                <div className="mt-4 pt-4 border-t-2 border-gray-300">
                                  <div className="flex justify-between items-center">
                                    <span className="text-xl font-bold text-gray-800">Итого:</span>
                                    <span className="text-2xl font-bold text-blue-600">
                                      {details.calculation.total_price.toFixed(2)} ₽
                                    </span>
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* Данные клиента и оплата */}
                            {(details.customer_name || details.customer_phone || details.advance_payment) && (
                              <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-200">
                                <h4 className="text-lg font-semibold text-gray-800 mb-4">
                                  Данные клиента
                                </h4>
                                <div className="space-y-2">
                                  {details.customer_name && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Имя:</span>
                                      <span className="font-medium text-gray-800">{details.customer_name}</span>
                                    </div>
                                  )}
                                  {details.customer_phone && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Телефон:</span>
                                      <span className="font-medium text-gray-800">{details.customer_phone}</span>
                                    </div>
                                  )}
                                  {details.payment_method && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Способ оплаты:</span>
                                      <span className="font-medium text-gray-800">{details.payment_method}</span>
                                    </div>
                                  )}
                                  <div className="pt-2 border-t border-blue-200">
                                    <div className="flex justify-between items-center">
                                      <span className="text-gray-600">Итого к оплате:</span>
                                      <span className="text-xl font-bold text-blue-600">
                                        {details.total_price.toFixed(2)} ₽
                                      </span>
                                    </div>
                                    {details.advance_payment > 0 && (
                                      <div className="flex justify-between items-center mt-2">
                                        <span className="text-gray-600">Аванс:</span>
                                        <span className="font-semibold text-green-600">
                                          {details.advance_payment.toFixed(2)} ₽
                                        </span>
                                      </div>
                                    )}
                                    {details.debt > 0 && (
                                      <div className="flex justify-between items-center mt-2">
                                        <span className="text-gray-600">Долг:</span>
                                        <span className="font-semibold text-red-600">
                                          {details.debt.toFixed(2)} ₽
                                        </span>
                                      </div>
                                    )}
                                    {details.debt === 0 && details.advance_payment > 0 && (
                                      <div className="mt-2 text-sm text-green-600 font-semibold">
                                        ✓ Оплачено полностью
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* Дополнительная информация */}
                            <div className="bg-white p-4 rounded-lg border-2 border-gray-200">
                              <p className="text-sm text-gray-500">
                                Обновлено: {details.updated_at || details.created_at}
                              </p>
                            </div>
                          </div>
                        ) : (
                          <div className="text-center py-8 text-red-600">
                            Не удалось загрузить детали заказа
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
