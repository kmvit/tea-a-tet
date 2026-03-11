import { createContext, useContext, useState, useCallback } from 'react';
import { calculatePrice } from '../api';

const OrderContext = createContext();

export const useOrder = () => {
  const context = useContext(OrderContext);
  if (!context) {
    throw new Error('useOrder must be used within OrderProvider');
  }
  return context;
};

export const OrderProvider = ({ children }) => {
  const [orderData, setOrderData] = useState({
    // Шаг 1: Размеры
    x1: null,
    x2: null,
    // Рамы (до 3 штук)
    frames: [
      {
        x1: null,
        x2: null,
        baguette_id: null,
        baguette_image: null,
        baguette_width: null,
        work_id: null,
      }
    ],
    passepartouts: [],
    // Шаг 2: Стекло, подкладка и натяжка
    glass_id: null,
    backing_id: null,
    stretch_id: null,
    podramnik_id: null,
    // Шаг 3: Доп. опции (молдинг, тросик, подвески)
    molding_id: null,
    molding_consumption: null,
    trosik_id: null,
    trosik_length: null,
    podveski_id: null,
    podveski_quantity: null,
    // Шаг 4: Фурнитура и упаковка
    hardware_id: null,
    hardware_quantity: 1,
    package_id: null,
    // Шаг 5: Данные клиента
    customer_name: null,
    customer_phone: null,
    payment_method: 'наличные',
    advance_payment: null,
    comment: null,
  });

  const [priceCalculation, setPriceCalculation] = useState(null);
  const [paintingImage, setPaintingImage] = useState(null);

  const updateOrderData = useCallback((updates) => {
    setOrderData((prev) => ({ ...prev, ...updates }));
  }, []);

  const calculateCurrentPrice = useCallback(async () => {
    try {
      // Определяем валидные x1, x2 (глобальные или из первой рамы)
      const x1 = orderData.x1 ?? orderData.frames?.[0]?.x1;
      const x2 = orderData.x2 ?? orderData.frames?.[0]?.x2;
      const x1Val = parseFloat(x1);
      const x2Val = parseFloat(x2);
      if (!x1 || !x2 || isNaN(x1Val) || isNaN(x2Val) || x1Val <= 0 || x2Val <= 0) {
        return null;
      }

      // Преобразуем данные для отправки на бэкенд
      const dataToSend = {
        x1: x1Val,
        x2: x2Val,
        glass_id: orderData.glass_id,
        backing_id: orderData.backing_id,
        hardware_id: orderData.hardware_id,
        hardware_quantity: orderData.hardware_quantity,
        podramnik_id: orderData.podramnik_id,
        package_id: orderData.package_id,
        molding_id: orderData.molding_id,
        molding_consumption: orderData.molding_consumption,
        trosik_id: orderData.trosik_id,
        trosik_length: orderData.trosik_length,
        podveski_id: orderData.podveski_id,
        podveski_quantity: orderData.podveski_quantity,
        stretch_id: orderData.stretch_id,
      };
      
      // Если есть массив рамок, отправляем его (с валидными размерами в каждой раме)
      if (orderData.frames && orderData.frames.length > 0) {
        dataToSend.frames = orderData.frames.map((f) => ({
          ...f,
          x1: f.x1 ?? x1Val,
          x2: f.x2 ?? x2Val,
        }));
        dataToSend.passepartouts = orderData.passepartouts || [];
      } else {
        // Обратная совместимость: если нет массива, но есть старые поля
        if (orderData.baguette_id) {
          dataToSend.baguette_id = orderData.baguette_id;
          dataToSend.passepartout_id = orderData.passepartout_id;
          dataToSend.passepartout_length = orderData.passepartout_length;
          dataToSend.passepartout_width = orderData.passepartout_width;
        }
      }
      
      const response = await calculatePrice(dataToSend);
      setPriceCalculation(response.data);
      return response.data;
    } catch (error) {
      const msg = error.response?.data?.error || error.message;
      console.error('Ошибка расчета цены:', msg, error.response?.data);
      return null;
    }
  }, [orderData]);

  const resetOrder = useCallback(() => {
    setOrderData({
      x1: null,
      x2: null,
      frames: [
        {
          x1: null,
          x2: null,
          baguette_id: null,
          baguette_image: null,
          baguette_width: null,
          work_id: null,
        }
      ],
      passepartouts: [],
      glass_id: null,
      backing_id: null,
      stretch_id: null,
      hardware_id: null,
      hardware_quantity: 1,
      podramnik_id: null,
      package_id: null,
      molding_id: null,
      molding_consumption: null,
      trosik_id: null,
      trosik_length: null,
      podveski_id: null,
      podveski_quantity: null,
      customer_name: null,
      customer_phone: null,
      payment_method: 'наличные',
      advance_payment: null,
      comment: null,
    });
    setPriceCalculation(null);
    setPaintingImage(null);
  }, []);

  return (
    <OrderContext.Provider
      value={{
        orderData,
        updateOrderData,
        priceCalculation,
        calculateCurrentPrice,
        paintingImage,
        setPaintingImage,
        resetOrder,
      }}
    >
      {children}
    </OrderContext.Provider>
  );
};
