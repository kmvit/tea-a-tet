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
        passepartout_id: null,
        passepartout_length: null,
        passepartout_width: null,
        work_id: null,
      }
    ],
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
      // Преобразуем данные для отправки на бэкенд
      // Отправляем массив рамок, если он есть
      const dataToSend = {
        x1: orderData.x1,
        x2: orderData.x2,
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
      
      // Если есть массив рамок, отправляем его
      if (orderData.frames && orderData.frames.length > 0) {
        dataToSend.frames = orderData.frames;
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
      console.error('Ошибка расчета цены:', error);
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
          passepartout_id: null,
          passepartout_length: null,
          passepartout_width: null,
          work_id: null,
        }
      ],
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
