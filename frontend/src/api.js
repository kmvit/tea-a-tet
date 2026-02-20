import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Получение данных
export const getBaguettes = (search = '') => {
  const params = search ? { params: { search } } : {};
  return api.get('/baguettes/', params);
};
export const getGlasses = () => api.get('/glasses/');
export const getBackings = () => api.get('/backings/');
export const getHardware = () => api.get('/hardware/');
export const getPodramniki = () => api.get('/podramniki/');
export const getPackages = () => api.get('/packages/');
export const getMoldings = () => api.get('/moldings/');
export const getTrosiki = () => api.get('/trosiki/');
export const getPodveski = () => api.get('/podveski/');
export const getPassepartout = () => api.get('/passepartout/');
export const getStretches = () => api.get('/stretches/');
export const getWorks = () => api.get('/works/');

// Расчет цены
export const calculatePrice = (data) => api.post('/calculate-price/', data);

// Создание заказа
export const createOrder = (data) => api.post('/create-order/', data);

// Получение списка заказов
export const getOrders = () => api.get('/orders/');

// Получение детальной информации о заказе
export const getOrderDetail = (orderId) => api.get(`/orders/${orderId}/`);

// Изменение статуса заказа
export const updateOrderStatus = (orderId, status) => api.patch(`/orders/${orderId}/status/`, { status });

// Генерация квитанции (Word документ)
export const generateReceipt = async (orderId) => {
  try {
    const response = await api.get(`/orders/${orderId}/receipt/`, {
      responseType: 'blob', // Важно для скачивания файла
    });
    
    // Проверяем, что это действительно файл, а не JSON с ошибкой
    if (response.data.type && response.data.type.includes('application/json')) {
      // Если это JSON, значит произошла ошибка
      const text = await response.data.text();
      const errorData = JSON.parse(text);
      throw new Error(errorData.error || 'Ошибка генерации квитанции');
    }
    
    // Создаем ссылку для скачивания
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `receipt_${orderId}.docx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    // Если это ошибка axios, пытаемся извлечь сообщение об ошибке
    if (error.response) {
      // Если ответ - blob, пытаемся прочитать его как JSON
      if (error.response.data instanceof Blob) {
        try {
          const text = await error.response.data.text();
          const errorData = JSON.parse(text);
          // Извлекаем сообщение об ошибке, включая traceback если есть
          let errorMessage = errorData.error || 'Ошибка генерации квитанции';
          if (errorData.traceback) {
            // Берем первую строку traceback для более понятного сообщения
            const tracebackLines = errorData.traceback.split('\n');
            const firstErrorLine = tracebackLines.find(line => 
              line.includes('Error') || line.includes('Exception') || line.includes('ValueError')
            );
            if (firstErrorLine) {
              errorMessage = `${errorMessage}\n${firstErrorLine.trim()}`;
            }
          }
          throw new Error(errorMessage);
        } catch (parseError) {
          throw new Error(`Ошибка генерации квитанции (${error.response.status})`);
        }
      } else if (error.response.data && error.response.data.error) {
        throw new Error(error.response.data.error);
      }
    }
    throw error;
  }
};

export default api;
