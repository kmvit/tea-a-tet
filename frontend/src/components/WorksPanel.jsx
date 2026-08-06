// Блок «Работы» — технологические операции по данным 1С.
// Все работы входят в стоимость заказа (оплачивает клиент).
export const WorksPanel = ({ works, className = '' }) => {
  if (!works || !works.items || works.items.length === 0) return null;

  return (
    <div className={`rounded-lg bg-gray-50 border border-gray-200 p-4 ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-semibold text-gray-700">Работы</h4>
        <span className="text-xs text-gray-400">входят в стоимость</span>
      </div>
      <div className="space-y-1">
        {works.items.map((w, i) => (
          <div key={i} className="flex justify-between text-sm text-gray-600">
            <span>{w.name}</span>
            <span className="font-medium tabular-nums">{w.total.toFixed(2)}</span>
          </div>
        ))}
      </div>
      <div className="flex justify-between text-sm font-semibold text-gray-800 mt-2 pt-2 border-t border-gray-200">
        <span>Итого работ</span>
        <span className="tabular-nums">{works.total_rate.toFixed(2)}</span>
      </div>
      <div className="flex justify-between text-xs text-gray-500 mt-1">
        <span>Время работы</span>
        <span className="tabular-nums">{works.work_time_hours} ч</span>
      </div>
    </div>
  );
};
