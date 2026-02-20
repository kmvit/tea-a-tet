import { useOrder } from '../context/OrderContext';

const steps = [
  { number: 1, name: 'Размеры и багет' },
  { number: 2, name: 'Стекло и подрамник' },
  { number: 3, name: 'Доп. опции' },
  { number: 4, name: 'Фурнитура' },
  { number: 5, name: 'Данные клиента' },
];

export const ProgressBar = ({ currentStep, onStepClick }) => {
  const { orderData } = useOrder();

  // Если currentStep не передан, используем старую логику для обратной совместимости
  const getCurrentStep = () => {
    if (currentStep !== undefined) return currentStep;
    return 1;
  };

  const step = getCurrentStep();

  const isStepCompleted = (stepNumber) => {
    if (stepNumber === 1) {
      const hasFrames = orderData.frames && orderData.frames.length > 0;
      const hasBaguette = hasFrames && orderData.frames.some(f => f.baguette_id);
      return orderData.x1 && orderData.x2 && hasBaguette;
    }
    if (stepNumber === 2) return orderData.glass_id && orderData.backing_id;
    if (stepNumber === 3) return true; // Дополнительные опции опциональны
    if (stepNumber === 4) return true; // Фурнитура и упаковка опциональны
    if (stepNumber === 5) return orderData.customer_name && orderData.customer_phone;
    return false;
  };

  // Проверка доступности шага: шаг доступен, если все предыдущие шаги завершены
  const isStepAccessible = (stepNumber) => {
    // Шаг 1 всегда доступен
    if (stepNumber === 1) return true;
    // Для остальных шагов проверяем, что все предыдущие шаги завершены
    for (let i = 1; i < stepNumber; i++) {
      if (!isStepCompleted(i)) {
        return false;
      }
    }
    return true;
  };

  const handleStepClick = (stepNumber) => {
    if (onStepClick && isStepAccessible(stepNumber)) {
      onStepClick(stepNumber);
    }
  };

  return (
    <div className="max-w-4xl mx-auto mb-12">
      <div className="flex items-center justify-between">
        {steps.map((stepItem) => {
          const isCompleted = isStepCompleted(stepItem.number);
          const isCurrent = stepItem.number === step;
          const isAccessible = isStepAccessible(stepItem.number);

          return (
            <div key={stepItem.number} className="flex-1 mr-2 last:mr-0">
              {isAccessible ? (
                <button
                  type="button"
                  onClick={() => handleStepClick(stepItem.number)}
                  className="block w-full cursor-pointer hover:opacity-80 transition-opacity"
                  disabled={false}
                >
                  <div className="relative">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${
                        isCompleted || isCurrent ? 'bg-blue-600' : 'bg-gray-300'
                      }`}
                    ></div>
                    <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 text-center">
                      <div
                        className={`w-12 h-12 mx-auto rounded-full flex items-center justify-center font-bold text-lg transition-all duration-300 ${
                          isCompleted
                            ? 'bg-blue-600 text-white'
                            : isCurrent
                            ? 'bg-blue-600 text-white ring-4 ring-blue-200'
                            : 'bg-gray-300 text-gray-600'
                        }`}
                      >
                        {stepItem.number}
                      </div>
                      <div className="mt-2 text-xs font-medium text-gray-600">
                        {stepItem.name}
                      </div>
                    </div>
                  </div>
                </button>
              ) : (
                <div className="relative cursor-not-allowed opacity-60">
                  <div className="h-2 rounded-full bg-gray-300"></div>
                  <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 text-center">
                    <div className="w-12 h-12 mx-auto rounded-full flex items-center justify-center font-bold text-lg bg-gray-300 text-gray-600">
                      {stepItem.number}
                    </div>
                    <div className="mt-2 text-xs font-medium text-gray-600">
                      {stepItem.name}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
