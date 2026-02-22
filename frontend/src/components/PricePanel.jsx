import { useEffect, useRef } from 'react';
import { useOrder } from '../context/OrderContext';
import { FramePreview } from './FramePreview';

export const PricePanel = () => {
  const { orderData, priceCalculation, calculateCurrentPrice, paintingImage, setPaintingImage } = useOrder();
  const fileInputRef = useRef(null);
  useEffect(() => {
    if (orderData.x1 && orderData.x2) {
      calculateCurrentPrice();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orderData.x1, orderData.x2, orderData.frames]);

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 sticky top-8">
      <h3 className="text-2xl font-bold text-gray-800 mb-6">Расчет стоимости</h3>

      {/* Предпросмотр рамки */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Предпросмотр рамки
        </label>
        <div className="space-y-2 mb-2">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) {
                const url = URL.createObjectURL(f);
                setPaintingImage(url);
              }
              e.target.value = '';
            }}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            {paintingImage ? 'Заменить изображение картины' : 'Загрузить изображение картины'}
          </button>
          {paintingImage && (
            <button
              type="button"
              onClick={() => setPaintingImage(null)}
              className="text-sm text-gray-500 hover:text-gray-700 ml-2"
            >
              Убрать
            </button>
          )}
        </div>
        <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-4 bg-gray-50">
          <FramePreview showLabel={false} />
        </div>
      </div>

      {/* Детали расчета */}
      <div className="space-y-3 mb-6">
        {priceCalculation && priceCalculation.components ? (
          Object.entries(priceCalculation.components).map(([key, component]) => (
            <div key={key} className="flex justify-between text-sm">
              <span className="text-gray-600">{component.name}</span>
              <span className="font-medium">{component.total_price.toFixed(2)} ₽</span>
            </div>
          ))
        ) : (
          <div className="text-gray-600 text-center py-8">
            Заполните форму для расчета стоимости
          </div>
        )}
      </div>

      {/* Итого */}
      <div className="border-t-2 border-gray-200 pt-4">
        <div className="flex justify-between items-center">
          <span className="text-xl font-bold text-gray-800">Итого:</span>
          <span className="text-3xl font-bold text-blue-600">
            {priceCalculation?.total_price
              ? `${priceCalculation.total_price.toFixed(2)} ₽`
              : '0 ₽'}
          </span>
        </div>
      </div>
    </div>
  );
};
