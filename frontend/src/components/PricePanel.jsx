import { useEffect, useRef } from 'react';
import { useOrder } from '../context/OrderContext';

const FRAME_WIDTH = 80; // Фиксированная ширина рамки в пикселях
const CORNER_SEGMENT = 25; // Сегмент, отрезаемый от уголка и дублируемый по всей стороне (вертикально для левой/правой, горизонтально для верхней/нижней)

export const PricePanel = () => {
  const { orderData, priceCalculation, calculateCurrentPrice } = useOrder();
  const canvasRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    if (orderData.x1 && orderData.x2) {
      calculateCurrentPrice();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orderData.x1, orderData.x2, orderData.frames]);

  // Получаем данные выбранного багета из первой рамы
  const getSelectedBaguette = () => {
    // Берем первую раму, если она есть и в ней выбран багет
    if (orderData.frames && orderData.frames.length > 0) {
      const firstFrame = orderData.frames[0];
      if (firstFrame.baguette_id && firstFrame.baguette_image) {
        return {
          image: firstFrame.baguette_image,
          width: firstFrame.baguette_width,
        };
      }
    }
    // Обратная совместимость со старой структурой данных
    if (orderData.baguette_id && orderData.baguette_image) {
      return {
        image: orderData.baguette_image,
        width: orderData.baguette_width,
      };
    }
    return null;
  };

  // Функция для отрисовки рамки
  const drawFrame = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const container = containerRef.current;
    const maxWidth = container ? container.clientWidth - 20 : 400;
    const maxHeight = 400;
    
    let paintingWidth = 300;
    let paintingHeight = 200;
    
    const availableWidth = maxWidth - (FRAME_WIDTH * 2);
    const availableHeight = maxHeight - (FRAME_WIDTH * 2);
    
    // Используем размеры из формы (x1, x2)
    if (orderData.x1 && orderData.x2) {
      const x1 = parseFloat(orderData.x1);
      const x2 = parseFloat(orderData.x2);
      // Сохраняем пропорции
      const aspectRatio = x1 / x2;
      
      // Рассчитываем размеры с сохранением пропорций
      if (aspectRatio > 1) {
        // Горизонтальная картина (ширина > высоты)
        paintingWidth = availableWidth;
        paintingHeight = availableWidth / aspectRatio;
        // Проверяем, не превышает ли высота доступное пространство
        if (paintingHeight > availableHeight) {
          paintingHeight = availableHeight;
          paintingWidth = availableHeight * aspectRatio;
        }
      } else {
        // Вертикальная или квадратная картина (высота >= ширины)
        paintingHeight = availableHeight;
        paintingWidth = availableHeight * aspectRatio;
        // Проверяем, не превышает ли ширина доступное пространство
        if (paintingWidth > availableWidth) {
          paintingWidth = availableWidth;
          paintingHeight = availableWidth / aspectRatio;
        }
      }
    }
    
    // Размеры canvas с учетом рамки
    const canvasWidth = paintingWidth + (FRAME_WIDTH * 2);
    const canvasHeight = paintingHeight + (FRAME_WIDTH * 2);
    
    // Устанавливаем внутренние размеры canvas (в пикселях)
    // Эти размеры определяют разрешение canvas и пропорции
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    
    // Рассчитываем масштаб для отображения с сохранением пропорций
    // Canvas должен поместиться в доступное пространство
    const maxDisplayWidth = maxWidth;
    const maxDisplayHeight = maxHeight;
    
    const scaleX = maxDisplayWidth / canvasWidth;
    const scaleY = maxDisplayHeight / canvasHeight;
    const scale = Math.min(scaleX, scaleY, 1); // Не увеличиваем больше оригинала
    
    // Устанавливаем CSS размеры для отображения с сохранением пропорций
    const displayWidth = canvasWidth * scale;
    const displayHeight = canvasHeight * scale;
    
    canvas.style.width = displayWidth + 'px';
    canvas.style.height = displayHeight + 'px';
    
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);
    
    // Рисуем фон
    ctx.fillStyle = '#f8f9fa';
    ctx.fillRect(FRAME_WIDTH, FRAME_WIDTH, paintingWidth, paintingHeight);
    
    // Получаем данные багета из Wizard через глобальное состояние или пропсы
    // Пока используем простую рамку, если багет выбран
    const baguette = getSelectedBaguette();
    
    if (baguette && baguette.image) {
      const cornerImage = new Image();
      cornerImage.crossOrigin = 'anonymous';
      
      const savedCanvasWidth = canvasWidth;
      const savedCanvasHeight = canvasHeight;
      const savedPaintingWidth = paintingWidth;
      const savedPaintingHeight = paintingHeight;
      
      cornerImage.onload = function() {
        // Обновляем CSS размеры canvas при загрузке изображения багета
        const container = containerRef.current;
        const maxDisplayWidth = container ? container.clientWidth - 20 : 400;
        const maxDisplayHeight = 400;
        const scaleX = maxDisplayWidth / savedCanvasWidth;
        const scaleY = maxDisplayHeight / savedCanvasHeight;
        const scale = Math.min(scaleX, scaleY, 1);
        canvas.style.width = (savedCanvasWidth * scale) + 'px';
        canvas.style.height = (savedCanvasHeight * scale) + 'px';
        
        ctx.clearRect(0, 0, savedCanvasWidth, savedCanvasHeight);
        
        ctx.fillStyle = '#f8f9fa';
        ctx.fillRect(FRAME_WIDTH, FRAME_WIDTH, savedPaintingWidth, savedPaintingHeight);
        
        const cornerSize = FRAME_WIDTH;
        
        // Рисуем уголки
        // 1. Нижний левый
        ctx.drawImage(cornerImage, 0, savedCanvasHeight - cornerSize, cornerSize, cornerSize);
        
        // 2. Верхний левый (поворот на 90°)
        ctx.save();
        ctx.translate(cornerSize / 2, cornerSize / 2);
        ctx.rotate(Math.PI / 2);
        ctx.drawImage(cornerImage, -cornerSize / 2, -cornerSize / 2, cornerSize, cornerSize);
        ctx.restore();
        
        // 3. Верхний правый (поворот на 180°)
        ctx.save();
        ctx.translate(savedCanvasWidth - cornerSize / 2, cornerSize / 2);
        ctx.rotate(Math.PI);
        ctx.drawImage(cornerImage, -cornerSize / 2, -cornerSize / 2, cornerSize, cornerSize);
        ctx.restore();
        
        // 4. Нижний правый (поворот на -90°)
        ctx.save();
        ctx.translate(savedCanvasWidth - cornerSize / 2, savedCanvasHeight - cornerSize / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.drawImage(cornerImage, -cornerSize / 2, -cornerSize / 2, cornerSize, cornerSize);
        ctx.restore();
        
        // Создаём паттерн для вертикальных сторон (левая/правая): сегмент 80×30 в canvas-координатах
        const verticalPatternCanvas = document.createElement('canvas');
        verticalPatternCanvas.width = cornerSize;
        verticalPatternCanvas.height = CORNER_SEGMENT;
        const vCtx = verticalPatternCanvas.getContext('2d');
        vCtx.drawImage(cornerImage, 0, 0, cornerImage.width, cornerImage.height * CORNER_SEGMENT / cornerSize, 0, 0, cornerSize, CORNER_SEGMENT);
        const verticalPattern = ctx.createPattern(verticalPatternCanvas, 'repeat-y');

        // Заполняем левую сторону — паттерн тиражируется без растяжения
        ctx.save();
        ctx.translate(0, cornerSize);
        ctx.fillStyle = verticalPattern;
        ctx.fillRect(0, 0, cornerSize, savedCanvasHeight - cornerSize * 2);
        ctx.restore();

        // Заполняем правую сторону — зеркально
        ctx.save();
        ctx.translate(savedCanvasWidth, cornerSize);
        ctx.scale(-1, 1);
        ctx.fillStyle = verticalPattern;
        ctx.fillRect(0, 0, cornerSize, savedCanvasHeight - cornerSize * 2);
        ctx.restore();

        // Создаём паттерн для горизонтальных сторон (верхняя/нижняя): сегмент 30×80 в canvas-координатах
        const horizontalPatternCanvas = document.createElement('canvas');
        horizontalPatternCanvas.width = CORNER_SEGMENT;
        horizontalPatternCanvas.height = cornerSize;
        const hCtx = horizontalPatternCanvas.getContext('2d');
        hCtx.drawImage(cornerImage, cornerImage.width - cornerImage.width * CORNER_SEGMENT / cornerSize, 0, cornerImage.width * CORNER_SEGMENT / cornerSize, cornerImage.height, 0, 0, CORNER_SEGMENT, cornerSize);
        const horizontalPattern = ctx.createPattern(horizontalPatternCanvas, 'repeat-x');

        // Заполняем верхнюю сторону
        ctx.save();
        ctx.translate(cornerSize, FRAME_WIDTH);
        ctx.scale(1, -1);
        ctx.fillStyle = horizontalPattern;
        ctx.fillRect(0, 0, savedCanvasWidth - cornerSize * 2, cornerSize);
        ctx.restore();

        // Заполняем нижнюю сторону — зеркально
        ctx.save();
        ctx.translate(savedCanvasWidth - cornerSize, savedCanvasHeight - FRAME_WIDTH);
        ctx.scale(-1, 1);
        ctx.fillStyle = horizontalPattern;
        ctx.fillRect(0, 0, savedCanvasWidth - cornerSize * 2, cornerSize);
        ctx.restore();
      };
      
      cornerImage.onerror = function() {
        // Обновляем CSS размеры canvas при ошибке загрузки
        const container = containerRef.current;
        const maxDisplayWidth = container ? container.clientWidth - 20 : 400;
        const maxDisplayHeight = 400;
        const scaleX = maxDisplayWidth / savedCanvasWidth;
        const scaleY = maxDisplayHeight / savedCanvasHeight;
        const scale = Math.min(scaleX, scaleY, 1);
        canvas.style.width = (savedCanvasWidth * scale) + 'px';
        canvas.style.height = (savedCanvasHeight * scale) + 'px';
        
        ctx.strokeStyle = '#8b5cf6';
        ctx.lineWidth = FRAME_WIDTH;
        ctx.strokeRect(FRAME_WIDTH / 2, FRAME_WIDTH / 2, paintingWidth + FRAME_WIDTH, paintingHeight + FRAME_WIDTH);
      };
      
      cornerImage.src = baguette.image;
    } else {
      // Проверяем, есть ли багет в первой раме или в старой структуре
      const hasBaguette = (orderData.frames && orderData.frames.length > 0 && orderData.frames[0].baguette_id) || orderData.baguette_id;
      
      if (hasBaguette) {
        // Простая рамка, если багет выбран, но нет изображения
        // Обновляем CSS размеры canvas
        const maxDisplayWidth = maxWidth;
        const maxDisplayHeight = maxHeight;
        const scaleX = maxDisplayWidth / canvasWidth;
        const scaleY = maxDisplayHeight / canvasHeight;
        const scale = Math.min(scaleX, scaleY, 1);
        canvas.style.width = (canvasWidth * scale) + 'px';
        canvas.style.height = (canvasHeight * scale) + 'px';
        
        ctx.strokeStyle = '#8b5cf6';
        ctx.lineWidth = FRAME_WIDTH;
        ctx.strokeRect(FRAME_WIDTH / 2, FRAME_WIDTH / 2, paintingWidth + FRAME_WIDTH, paintingHeight + FRAME_WIDTH);
      }
    }
  };

  // Отрисовываем рамку при изменении данных
  useEffect(() => {
    // Проверяем наличие багета в новой структуре (frames) или старой (baguette_id)
    const hasBaguette = (orderData.frames && orderData.frames.length > 0 && orderData.frames[0].baguette_id) || orderData.baguette_id;
    const baguetteImage = (orderData.frames && orderData.frames.length > 0 && orderData.frames[0].baguette_image) || orderData.baguette_image;
    
    // Отрисовываем рамку если есть размеры картины или выбран багет
    if (orderData.x1 && orderData.x2 || hasBaguette) {
      // Небольшая задержка для обновления размеров контейнера
      const timeout = setTimeout(() => {
        drawFrame();
      }, 100);
      return () => clearTimeout(timeout);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orderData.x1, orderData.x2, orderData.frames, orderData.baguette_id, orderData.baguette_image]);

  // Обработка изменения размера окна
  useEffect(() => {
    const handleResize = () => {
      const hasBaguette = (orderData.frames && orderData.frames.length > 0 && orderData.frames[0].baguette_id) || orderData.baguette_id;
      if (orderData.x1 && orderData.x2 || hasBaguette) {
        setTimeout(() => {
          drawFrame();
        }, 100);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orderData.x1, orderData.x2, orderData.frames, orderData.baguette_id]);

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 sticky top-8">
      <h3 className="text-2xl font-bold text-gray-800 mb-6">Расчет стоимости</h3>

      {/* Предпросмотр рамки */}
      <div className="mb-6" ref={containerRef}>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Предпросмотр рамки
        </label>
        <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-4 bg-gray-50">
          {(orderData.x1 && orderData.x2) || (orderData.frames && orderData.frames.length > 0 && orderData.frames[0].baguette_id) || orderData.baguette_id ? (
            <div className="relative w-full flex justify-center">
              <canvas
                ref={canvasRef}
                className="block rounded-lg"
                style={{ 
                  maxWidth: '100%',
                  maxHeight: '400px'
                }}
              />
            </div>
          ) : (
            <div className="py-8 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <p className="mt-2 text-sm text-gray-600">Укажите размеры и выберите багет</p>
            </div>
          )}
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
