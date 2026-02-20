import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useOrder } from '../context/OrderContext';
import {
  getBaguettes,
  getGlasses,
  getBackings,
  getHardware,
  getPodramniki,
  getPackages,
  getMoldings,
  getTrosiki,
  getPodveski,
  getPassepartout,
  getStretches,
} from '../api';
import { ProgressBar } from '../components/ProgressBar';
import { PricePanel } from '../components/PricePanel';

export const Wizard = () => {
  const navigate = useNavigate();
  const { orderData, updateOrderData, calculateCurrentPrice, priceCalculation } = useOrder();
  const [currentStep, setCurrentStep] = useState(1);

  // Данные для всех шагов
  const [baguettes, setBaguettes] = useState([]);
  const [glasses, setGlasses] = useState([]);
  const [backings, setBackings] = useState([]);
  const [hardware, setHardware] = useState([]);
  const [podramniki, setPodramniki] = useState([]);
  const [packages, setPackages] = useState([]);
  const [moldings, setMoldings] = useState([]);
  const [trosiki, setTrosiki] = useState([]);
  const [podveski, setPodveski] = useState([]);
  const [passepartout, setPassepartout] = useState([]);
  const [stretches, setStretches] = useState([]);

  const [loading, setLoading] = useState(true);

  // Локальное состояние для каждого шага
  const [x1, setX1] = useState(orderData.x1 || '');
  const [x2, setX2] = useState(orderData.x2 || '');
  const [errors, setErrors] = useState({});
  // Массив рамок (до 3 штук)
  const [frames, setFrames] = useState(
    orderData.frames && orderData.frames.length > 0
      ? orderData.frames.map((f) => ({
          ...f,
          x1: f.x1 ?? orderData.x1,
          x2: f.x2 ?? orderData.x2,
        }))
      : [
          {
            x1: orderData.x1 ?? null,
            x2: orderData.x2 ?? null,
            baguette_id: null,
            baguette_image: null,
            baguette_width: null,
            baguette_name: null,
            passepartout_id: null,
            passepartout_length: null,
            passepartout_width: null,
            work_id: null,
          }
        ]
  );
  // Поиск багетов для каждой рамы
  const [baguetteSearches, setBaguetteSearches] = useState(['']);
  const baguetteSearchTimeoutRef = useRef(null);
  const baguetteSearchInputRef = useRef(null);
  const [openBaguetteDropdownFrame, setOpenBaguetteDropdownFrame] = useState(null);
  const baguetteDropdownRef = useRef(null);

  const [glassId, setGlassId] = useState(orderData.glass_id || '');
  const [backingId, setBackingId] = useState(orderData.backing_id || '');
  const [hardwareId, setHardwareId] = useState(orderData.hardware_id || '');
  const [hardwareQuantity, setHardwareQuantity] = useState(
    orderData.hardware_quantity || 1
  );
  const [podramnikId, setPodramnikId] = useState(
    orderData.podramnik_id || ''
  );
  const [packageId, setPackageId] = useState(orderData.package_id || '');
  const [moldingId, setMoldingId] = useState(orderData.molding_id || '');
  const [moldingConsumption, setMoldingConsumption] = useState(
    orderData.molding_consumption || ''
  );
  const [trosikId, setTrosikId] = useState(orderData.trosik_id || '');
  const [trosikLength, setTrosikLength] = useState(
    orderData.trosik_length || ''
  );
  const [podveskiId, setPodveskiId] = useState(orderData.podveski_id || '');
  const [podveskiQuantity, setPodveskiQuantity] = useState(
    orderData.podveski_quantity || ''
  );
  const [stretchId, setStretchId] = useState(orderData.stretch_id || '');
  
  // Шаг 5: Данные клиента
  const [customerName, setCustomerName] = useState(orderData.customer_name || '');
  const [customerPhone, setCustomerPhone] = useState(orderData.customer_phone || '');
  const [paymentMethod, setPaymentMethod] = useState(orderData.payment_method || 'наличные');
  const [advancePayment, setAdvancePayment] = useState(orderData.advance_payment || '');

  // Загрузка всех данных при монтировании
  useEffect(() => {
    const fetchAllData = async () => {
      try {
        const [
          baguettesRes,
          glassesRes,
          backingsRes,
          hardwareRes,
          podramnikiRes,
          packagesRes,
          moldingsRes,
          trosikiRes,
          podveskiRes,
          passepartoutRes,
          stretchesRes,
        ] = await Promise.all([
          getBaguettes(),
          getGlasses(),
          getBackings(),
          getHardware(),
          getPodramniki(),
          getPackages(),
          getMoldings(),
          getTrosiki(),
          getPodveski(),
          getPassepartout(),
          getStretches(),
        ]);

        setBaguettes(baguettesRes.data);
        setGlasses(glassesRes.data);
        setBackings(backingsRes.data);
        setHardware(hardwareRes.data);
        setPodramniki(podramnikiRes.data);
        setPackages(packagesRes.data);
        setMoldings(moldingsRes.data);
        setTrosiki(trosikiRes.data);
        setPodveski(podveskiRes.data);
        setPassepartout(passepartoutRes.data);
        setStretches(stretchesRes.data);
      } catch (error) {
        console.error('Ошибка загрузки данных:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, []);

  // Автопоиск багетов с debounce (300 мс)
  const debouncedFetchBaguettes = useCallback((query) => {
    if (baguetteSearchTimeoutRef.current) {
      clearTimeout(baguetteSearchTimeoutRef.current);
    }
    baguetteSearchTimeoutRef.current = setTimeout(async () => {
      try {
        const baguettesRes = await getBaguettes(query);
        setBaguettes(baguettesRes.data);
      } catch (error) {
        console.error('Ошибка загрузки багетов:', error);
      }
      baguetteSearchTimeoutRef.current = null;
    }, 300);
  }, []);

  // Мгновенная загрузка багетов (при фокусе на поле)
  const fetchBaguettesImmediate = useCallback(async (query) => {
    try {
      const baguettesRes = await getBaguettes(query);
      setBaguettes(baguettesRes.data);
    } catch (error) {
      console.error('Ошибка загрузки багетов:', error);
    }
  }, []);

  // Очистка таймера при размонтировании
  useEffect(() => {
    return () => {
      if (baguetteSearchTimeoutRef.current) {
        clearTimeout(baguetteSearchTimeoutRef.current);
      }
    };
  }, []);

  // Автофокус на поле поиска багета при отображении шага 1
  useEffect(() => {
    if (currentStep === 1 && baguetteSearchInputRef.current) {
      baguetteSearchInputRef.current.focus();
    }
  }, [currentStep]);

  // Закрытие выпадающего списка багетов при клике снаружи
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (baguetteDropdownRef.current && !baguetteDropdownRef.current.contains(e.target)) {
        setOpenBaguetteDropdownFrame(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Автоматический пересчет цены при изменении данных заказа
  useEffect(() => {
    if (orderData.x1 && orderData.x2) {
      calculateCurrentPrice();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orderData.x1, orderData.x2, orderData.frames, orderData.glass_id, orderData.backing_id, orderData.podramnik_id, orderData.hardware_id, orderData.package_id]);

  // Синхронизация локального состояния с orderData
  useEffect(() => {
    if (orderData.frames && orderData.frames.length > 0 && frames.length === 0) {
      setFrames(orderData.frames);
      setBaguetteSearches(orderData.frames.map(() => ''));
    }
    if (orderData.glass_id && !glassId) {
      setGlassId(String(orderData.glass_id));
    }
    if (orderData.backing_id && !backingId) {
      setBackingId(String(orderData.backing_id));
    }
    if (orderData.x2 && !x2) {
      setX2(String(orderData.x2));
    }
    // Синхронизация данных клиента
    if (orderData.customer_name && !customerName) {
      setCustomerName(orderData.customer_name);
    }
    if (orderData.customer_phone && !customerPhone) {
      setCustomerPhone(orderData.customer_phone);
    }
    if (orderData.payment_method && !paymentMethod) {
      setPaymentMethod(orderData.payment_method);
    }
    if (orderData.advance_payment && !advancePayment) {
      setAdvancePayment(String(orderData.advance_payment));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orderData]);

  // Автоматическая установка длины тросика равной ширине картины (x2)
  useEffect(() => {
    if (trosikId && x2) {
      setTrosikLength(x2);
    }
  }, [trosikId, x2]);

  // Обработчики для каждого шага
  // Шаг 1: Размеры и рамки (багет + паспарту)
  const handleStep1Submit = (e) => {
    e.preventDefault();
    const newErrors = {};

    if (frames.length === 1) {
      if (!x1 || parseFloat(x1) <= 0) {
        newErrors.x1 = 'Введите корректный размер X1';
      }
      if (!x2 || parseFloat(x2) <= 0) {
        newErrors.x2 = 'Введите корректный размер X2';
      }
    } else {
      for (let i = 0; i < frames.length; i++) {
        const f = frames[i];
        if (f.baguette_id) {
          const vx1 = parseFloat(f.x1);
          const vx2 = parseFloat(f.x2);
          if (!f.x1 || !vx1 || vx1 <= 0) newErrors[`frame_${i}_x1`] = `Рама ${i + 1}: введите размер X1`;
          if (!f.x2 || !vx2 || vx2 <= 0) newErrors[`frame_${i}_x2`] = `Рама ${i + 1}: введите размер X2`;
        }
      }
    }

    const hasBaguette = frames.some(frame => frame.baguette_id);
    if (!hasBaguette) {
      newErrors.frames = 'Выберите багет хотя бы в одной раме';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    const finalFrames = frames.length === 1
      ? [{ ...frames[0], x1: parseFloat(x1), x2: parseFloat(x2) }]
      : frames.map((f) => ({ ...f, x1: parseFloat(f.x1), x2: parseFloat(f.x2) }));

    updateOrderData({
      x1: finalFrames[0]?.x1 ?? parseFloat(x1),
      x2: finalFrames[0]?.x2 ?? parseFloat(x2),
      frames: finalFrames,
    });
    setCurrentStep(2);
  };

  // Добавление новой рамы
  const addFrame = () => {
    if (frames.length < 3) {
      const newFrame = {
        x1: null,
        x2: null,
        baguette_id: null,
        baguette_image: null,
        baguette_width: null,
        baguette_name: null,
        passepartout_id: null,
        passepartout_length: null,
        passepartout_width: null,
        work_id: null,
      };
      setFrames([...frames, newFrame]);
      setBaguetteSearches([...baguetteSearches, '']);
    }
  };

  // Удаление рамы
  const removeFrame = (index) => {
    if (frames.length > 1) {
      const newFrames = frames.filter((_, i) => i !== index);
      setFrames(newFrames);
      const newSearches = baguetteSearches.filter((_, i) => i !== index);
      setBaguetteSearches(newSearches);
      // Обновляем orderData
      updateOrderData({ frames: newFrames });
    }
  };

  // Обновление рамы
  const updateFrame = (index, updates) => {
    const newFrames = [...frames];
    newFrames[index] = { ...newFrames[index], ...updates };
    setFrames(newFrames);
    const orderUpdates = { frames: newFrames };
    // При нескольких рамах синхронизируем x1, x2 из первой рамы для расчёта цены
    if (newFrames.length > 1 && newFrames[0]?.x1 != null && newFrames[0]?.x2 != null) {
      orderUpdates.x1 = parseFloat(newFrames[0].x1);
      orderUpdates.x2 = parseFloat(newFrames[0].x2);
    }
    updateOrderData(orderUpdates);
  };

  // Обновление поиска багетов для конкретной рамы
  const updateBaguetteSearch = (index, searchValue) => {
    const newSearches = [...baguetteSearches];
    newSearches[index] = searchValue;
    setBaguetteSearches(newSearches);
  };

  // Шаг 2: Стекло, подкладка и подрамник вместе
  const handleStep2Submit = (e) => {
    e.preventDefault();
    if (!glassId || !backingId) {
      return;
    }

    updateOrderData({
      glass_id: parseInt(glassId),
      backing_id: parseInt(backingId),
      podramnik_id: podramnikId ? parseInt(podramnikId) : null,
      stretch_id: stretchId ? parseInt(stretchId) : null,
    });
    setCurrentStep(3);
  };

  // Шаг 3: Дополнительные опции (молдинг, тросик, подвески)
  const handleStep3Submit = (e) => {
    e.preventDefault();

    const updates = {};

    if (moldingId && moldingConsumption) {
      updates.molding_id = parseInt(moldingId);
      updates.molding_consumption = parseFloat(moldingConsumption);
    } else {
      updates.molding_id = null;
      updates.molding_consumption = null;
    }

    if (trosikId) {
      updates.trosik_id = parseInt(trosikId);
      // Длина тросика равна ширине картины (x2)
      updates.trosik_length = parseFloat(trosikLength || x2 || 0);
    } else {
      updates.trosik_id = null;
      updates.trosik_length = null;
    }

    if (podveskiId) {
      updates.podveski_id = parseInt(podveskiId);
      // Количество подвесок автоматически устанавливается в 1
      updates.podveski_quantity = 1;
    } else {
      updates.podveski_id = null;
      updates.podveski_quantity = null;
    }

    updateOrderData(updates);
    setCurrentStep(4);
  };

  // Шаг 4: Фурнитура и упаковка
  const handleStep4Submit = (e) => {
    e.preventDefault();

    const updates = {};

    if (hardwareId) {
      updates.hardware_id = parseInt(hardwareId);
      updates.hardware_quantity = parseInt(hardwareQuantity);
    } else {
      updates.hardware_id = null;
      updates.hardware_quantity = 1;
    }

    if (packageId) {
      updates.package_id = parseInt(packageId);
    } else {
      updates.package_id = null;
    }

    updateOrderData(updates);
    setCurrentStep(5);
  };
  
  // Шаг 5: Данные клиента
  const handleStep5Submit = (e) => {
    e.preventDefault();

    // Валидация
    if (!customerName.trim()) {
      setErrors({ customer_name: 'Введите имя клиента' });
      return;
    }
    if (!customerPhone.trim()) {
      setErrors({ customer_phone: 'Введите телефон клиента' });
      return;
    }

    const updates = {
      customer_name: customerName.trim(),
      customer_phone: customerPhone.trim(),
      payment_method: paymentMethod,
      advance_payment: advancePayment ? parseFloat(advancePayment) : null,
    };

    updateOrderData(updates);
    navigate('/summary');
  };


  // Проверка завершенности шага (та же логика, что в ProgressBar)
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

  const goToStep = (step) => {
    // Проверка доступности шага перед переходом
    if (isStepAccessible(step)) {
      setCurrentStep(step);
    }
  };

  if (loading) {
    return (
      <div className="wizard-loading flex items-center justify-center py-20">
        <div className="text-xl text-gray-600">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="wizard-page py-8">
      <div className="container mx-auto px-4">
        <div className="py-[50px]">
          <ProgressBar currentStep={currentStep} onStepClick={goToStep} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="wizard-card p-8">
              {/* Шаг 1: Размеры, паспарту и багет */}
              {currentStep === 1 && (
                <>
                  <h2 className="text-3xl font-bold text-gray-800 mb-6">
                    📏 Шаг 1: Укажите размеры и выберите багет
                  </h2>
                  <form onSubmit={handleStep1Submit} className="space-y-6">
                    <div className="space-y-6">
                      {/* Размеры — только для одной рамы */}
                      {frames.length === 1 && (
                        <div className="wizard-section p-6">
                          <h3 className="text-xl font-semibold text-gray-800 mb-4">
                            Размеры картины
                          </h3>
                          <div className="space-y-4">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Размер X1 (см)
                              </label>
                              <input
                                type="number"
                                step="0.01"
                                min="0.01"
                                value={x1}
                                onChange={(e) => {
                                  const newX1 = e.target.value;
                                  setX1(newX1);
                                  setErrors({ ...errors, x1: null });
                                  if (newX1 && parseFloat(newX1) > 0) {
                                    updateOrderData({ x1: parseFloat(newX1) });
                                  }
                                }}
                                className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-blue-200 transition ${
                                  errors.x1 ? 'border-red-500' : 'border-gray-300 focus:border-blue-500'
                                }`}
                                placeholder="Введите размер X1"
                              />
                              {errors.x1 && (
                                <p className="mt-1 text-sm text-red-600">{errors.x1}</p>
                              )}
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Размер X2 (см)
                              </label>
                              <input
                                type="number"
                                step="0.01"
                                min="0.01"
                                value={x2}
                                onChange={(e) => {
                                  const newX2 = e.target.value;
                                  setX2(newX2);
                                  setErrors({ ...errors, x2: null });
                                  if (newX2 && parseFloat(newX2) > 0) {
                                    updateOrderData({ x2: parseFloat(newX2) });
                                  }
                                }}
                                className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-blue-200 transition ${
                                  errors.x2 ? 'border-red-500' : 'border-gray-300 focus:border-blue-500'
                                }`}
                                placeholder="Введите размер X2"
                              />
                              {errors.x2 && (
                                <p className="mt-1 text-sm text-red-600">{errors.x2}</p>
                              )}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Рамы */}
                      {frames.map((frame, frameIndex) => (
                        <div key={frameIndex} className="wizard-frame-card p-6">
                          <div className="flex justify-between items-center mb-4">
                            <h3 className="text-xl font-semibold text-gray-800">
                              Рама {frameIndex + 1}
                            </h3>
                            {frames.length > 1 && (
                              <button
                                type="button"
                                onClick={() => removeFrame(frameIndex)}
                                className="text-red-600 hover:text-red-800 text-sm font-medium"
                              >
                                Удалить раму
                              </button>
                            )}
                          </div>

                          {/* Размеры рамы — при нескольких рамах у каждой свои размеры */}
                          {frames.length > 1 && (
                            <div className="mb-6 grid grid-cols-2 gap-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                  Размер X1 (см)
                                </label>
                                <input
                                  type="number"
                                  step="0.01"
                                  min="0.01"
                                  value={frame.x1 ?? ''}
                                  onChange={(e) => {
                                    const v = e.target.value;
                                    updateFrame(frameIndex, {
                                      x1: v && parseFloat(v) > 0 ? parseFloat(v) : null,
                                    });
                                    setErrors({ ...errors, [`frame_${frameIndex}_x1`]: null });
                                  }}
                                  className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-blue-200 transition ${
                                    errors[`frame_${frameIndex}_x1`]
                                      ? 'border-red-500'
                                      : 'border-gray-300 focus:border-blue-500'
                                  }`}
                                  placeholder="X1"
                                />
                                {errors[`frame_${frameIndex}_x1`] && (
                                  <p className="mt-1 text-sm text-red-600">
                                    {errors[`frame_${frameIndex}_x1`]}
                                  </p>
                                )}
                              </div>
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                  Размер X2 (см)
                                </label>
                                <input
                                  type="number"
                                  step="0.01"
                                  min="0.01"
                                  value={frame.x2 ?? ''}
                                  onChange={(e) => {
                                    const v = e.target.value;
                                    updateFrame(frameIndex, {
                                      x2: v && parseFloat(v) > 0 ? parseFloat(v) : null,
                                    });
                                    setErrors({ ...errors, [`frame_${frameIndex}_x2`]: null });
                                  }}
                                  className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-blue-200 transition ${
                                    errors[`frame_${frameIndex}_x2`]
                                      ? 'border-red-500'
                                      : 'border-gray-300 focus:border-blue-500'
                                  }`}
                                  placeholder="X2"
                                />
                                {errors[`frame_${frameIndex}_x2`] && (
                                  <p className="mt-1 text-sm text-red-600">
                                    {errors[`frame_${frameIndex}_x2`]}
                                  </p>
                                )}
                              </div>
                            </div>
                          )}

                          <div className="space-y-6">
                            {/* Багет — объединённый поиск и выбор */}
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Поиск и выбор багета
                              </label>
                              <div
                                ref={(el) => {
                                  if (openBaguetteDropdownFrame === frameIndex) {
                                    baguetteDropdownRef.current = el;
                                  }
                                }}
                                className="relative"
                              >
                                <input
                                  ref={frameIndex === 0 ? baguetteSearchInputRef : null}
                                  type="text"
                                  value={
                                    frame.baguette_id
                                      ? (frame.baguette_name ||
                                          (() => {
                                            const b = baguettes.find((x) => String(x.id) === String(frame.baguette_id));
                                            return b ? `${b.name}${b.barcode ? ` (${b.barcode})` : ''} — ${b.price} ₽/м` : '';
                                          })())
                                      : (baguetteSearches[frameIndex] || '')
                                  }
                                  onChange={(e) => {
                                    const value = e.target.value;
                                    if (frame.baguette_id) {
                                      updateFrame(frameIndex, {
                                        baguette_id: null,
                                        baguette_image: null,
                                        baguette_width: null,
                                        baguette_name: null,
                                      });
                                    }
                                    updateBaguetteSearch(frameIndex, value);
                                    debouncedFetchBaguettes(value);
                                    setOpenBaguetteDropdownFrame(frameIndex);
                                  }}
                                  onFocus={() => {
                                    setOpenBaguetteDropdownFrame(frameIndex);
                                    fetchBaguettesImmediate(baguetteSearches[frameIndex] || '');
                                  }}
                                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                                  placeholder="Введите название или штрихкод багета"
                                  autoComplete="off"
                                />
                                {openBaguetteDropdownFrame === frameIndex && (
                                  <ul className="absolute z-10 mt-1 w-full max-h-60 overflow-auto bg-white border-2 border-gray-300 rounded-lg shadow-lg">
                                    {baguettes.length === 0 ? (
                                      <li className="px-4 py-3 text-gray-500">
                                        {baguetteSearches[frameIndex] ? 'Ничего не найдено' : 'Введите название или штрихкод'}
                                      </li>
                                    ) : (
                                      baguettes.map((baguette) => (
                                        <li
                                          key={baguette.id}
                                          className="px-4 py-3 cursor-pointer hover:bg-blue-50 first:rounded-t-md last:rounded-b-md"
                                          onMouseDown={(e) => {
                                            e.preventDefault();
                                            const displayName = `${baguette.name}${baguette.barcode ? ` (${baguette.barcode})` : ''} — ${baguette.price} ₽/м`;
                                            updateFrame(frameIndex, {
                                              baguette_id: baguette.id,
                                              baguette_image: baguette.image || null,
                                              baguette_width: baguette.width || null,
                                              baguette_name: displayName,
                                            });
                                            updateBaguetteSearch(frameIndex, '');
                                            setOpenBaguetteDropdownFrame(null);
                                            setErrors({ ...errors, frames: null });
                                          }}
                                        >
                                          {baguette.name} {baguette.barcode && `(${baguette.barcode})`} — {baguette.price} ₽/м
                                        </li>
                                      ))
                                    )}
                                  </ul>
                                )}
                              </div>
                            </div>

                            {/* Паспарту */}
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Паспарту{' '}
                                <span className="text-sm font-normal text-gray-500">
                                  (опционально)
                                </span>
                              </label>
                              <div className="space-y-4">
                                <select
                                  value={frame.passepartout_id ? String(frame.passepartout_id) : ''}
                                  onChange={(e) => {
                                    updateFrame(frameIndex, {
                                      passepartout_id: e.target.value ? parseInt(e.target.value) : null,
                                    });
                                  }}
                                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                                >
                                  <option value="">-- Не выбрано --</option>
                                  {passepartout.map((pp) => (
                                    <option key={pp.id} value={pp.id}>
                                      {pp.name} ({pp.price} ₽)
                                    </option>
                                  ))}
                                </select>
                                {frame.passepartout_id && (
                                  <>
                                    <div>
                                      <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Длина паспарту (см)
                                      </label>
                                      <input
                                        type="number"
                                        step="0.01"
                                        min="0.01"
                                        value={frame.passepartout_length || ''}
                                        onChange={(e) => {
                                          const newLength = e.target.value;
                                          updateFrame(frameIndex, {
                                            passepartout_length: newLength && parseFloat(newLength) > 0 ? parseFloat(newLength) : null,
                                          });
                                        }}
                                        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                                        placeholder="Введите длину паспарту"
                                      />
                                    </div>
                                    <div>
                                      <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Ширина паспарту (см)
                                      </label>
                                      <input
                                        type="number"
                                        step="0.01"
                                        min="0.01"
                                        value={frame.passepartout_width || ''}
                                        onChange={(e) => {
                                          const newWidth = e.target.value;
                                          updateFrame(frameIndex, {
                                            passepartout_width: newWidth && parseFloat(newWidth) > 0 ? parseFloat(newWidth) : null,
                                          });
                                        }}
                                        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                                        placeholder="Введите ширину паспарту"
                                      />
                                    </div>
                                  </>
                                )}
                              </div>
                            </div>

                          </div>
                        </div>
                      ))}

                      {/* Кнопка добавления рамы */}
                      {frames.length < 3 && (
                        <div className="flex justify-center">
                          <button
                            type="button"
                            onClick={addFrame}
                            className="wizard-button-add px-6 py-3 font-semibold"
                          >
                            + Добавить раму
                          </button>
                        </div>
                      )}

                      {errors.frames && (
                        <div className="wizard-error p-4">
                          <p className="text-sm text-red-600">{errors.frames}</p>
                        </div>
                      )}
                    </div>

                    <div className="wizard-callout p-4">
                      <div className="flex">
                        <div className="flex-shrink-0">
                          <svg
                            className="h-5 w-5 text-blue-500"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                          >
                            <path
                              fillRule="evenodd"
                              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                              clipRule="evenodd"
                            />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <p className="text-sm text-blue-700">
                            Введите размеры вашей картины в сантиметрах и выберите багет для каждой рамы (можно добавить до 3 рам). На
                            основе этих данных будет рассчитано количество
                            необходимых материалов.
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-end">
                      <button
                        type="submit"
                        className="wizard-button-primary px-8 py-3 font-semibold"
                      >
                        Далее →
                      </button>
                    </div>
                  </form>
                </>
              )}

              {/* Шаг 2: Стекло, подкладка и подрамник */}
              {currentStep === 2 && (
                <>
                  <h2 className="text-3xl font-bold text-gray-800 mb-6">
                    🔍 Шаг 2: Выберите стекло, подкладку и подрамник
                  </h2>

                  <form onSubmit={handleStep2Submit} className="space-y-6">
                    <div className="space-y-6">
                      {/* Стекло */}
                      <div className="wizard-section p-6">
                        <h3 className="text-xl font-semibold text-gray-800 mb-4">
                          Стекло
                        </h3>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Выберите стекло
                          </label>
                          <select
                            value={glassId}
                            onChange={(e) => {
                              const newGlassId = e.target.value;
                              setGlassId(newGlassId);
                              // Сразу обновляем orderData для пересчета цены
                              updateOrderData({
                                glass_id: newGlassId ? parseInt(newGlassId) : null,
                              });
                            }}
                            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                          >
                            <option value="">-- Выберите стекло --</option>
                            {glasses.map((glass) => (
                              <option key={glass.id} value={glass.id}>
                                {glass.name} ({glass.price_per_sqm} ₽/кв.м)
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>

                      {/* Подкладка */}
                      <div className="wizard-section p-6">
                        <h3 className="text-xl font-semibold text-gray-800 mb-4">
                          Подкладка
                        </h3>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Выберите подкладку
                          </label>
                          <select
                            value={backingId}
                            onChange={(e) => {
                              const newBackingId = e.target.value;
                              setBackingId(newBackingId);
                              // Сразу обновляем orderData для пересчета цены
                              updateOrderData({
                                backing_id: newBackingId ? parseInt(newBackingId) : null,
                              });
                            }}
                            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                          >
                            <option value="">-- Выберите подкладку --</option>
                            {backings.map((backing) => (
                              <option key={backing.id} value={backing.id}>
                                {backing.name} ({backing.price} ₽)
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>

                      {/* Подрамник */}
                      <div className="wizard-section p-6">
                        <h3 className="text-xl font-semibold text-gray-800 mb-4">
                          Подрамник{' '}
                          <span className="text-sm font-normal text-gray-500">
                            (опционально)
                          </span>
                        </h3>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Выберите подрамник
                          </label>
                          <select
                            value={podramnikId}
                            onChange={(e) => {
                              const newPodramnikId = e.target.value;
                              setPodramnikId(newPodramnikId);
                              // Сразу обновляем orderData для пересчета цены
                              updateOrderData({
                                podramnik_id: newPodramnikId ? parseInt(newPodramnikId) : null,
                              });
                            }}
                            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                          >
                            <option value="">-- Выберите подрамник --</option>
                            {podramniki.map((podramnik) => (
                              <option key={podramnik.id} value={podramnik.id}>
                                {podramnik.name} ({podramnik.price} ₽)
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>

                      {/* Натяжка */}
                      <div className="wizard-section p-6">
                        <h3 className="text-xl font-semibold text-gray-800 mb-4">
                          Натяжка{' '}
                          <span className="text-sm font-normal text-gray-500">
                            (опционально)
                          </span>
                        </h3>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Выберите натяжку
                          </label>
                          <select
                            value={stretchId}
                            onChange={(e) => {
                              const newStretchId = e.target.value;
                              setStretchId(newStretchId);
                              // Сразу обновляем orderData для пересчета цены
                              updateOrderData({
                                stretch_id: newStretchId ? parseInt(newStretchId) : null,
                              });
                            }}
                            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                          >
                            <option value="">-- Выберите натяжку --</option>
                            {stretches.map((stretch) => (
                              <option key={stretch.id} value={stretch.id}>
                                {stretch.name} ({stretch.price_per_sqm} ₽/кв.м)
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-between pt-4">
                      <button
                        type="button"
                        onClick={() => setCurrentStep(1)}
                        className="wizard-button-secondary px-8 py-3 font-semibold"
                      >
                        ← Назад
                      </button>
                      <button
                        type="submit"
                        disabled={!glassId || !backingId}
                        className="wizard-button-primary px-8 py-3 font-semibold disabled:cursor-not-allowed"
                      >
                        Далее →
                      </button>
                    </div>
                  </form>
                </>
              )}

              {/* Шаг 3: Дополнительные опции */}
              {currentStep === 3 && (
                <>
                  <h2 className="text-3xl font-bold text-gray-800 mb-6">
                    ✨ Шаг 3: Дополнительные опции (опционально)
                  </h2>

                  <div className="wizard-callout p-4 mb-6">
                    <p className="text-sm text-blue-700">
                      <strong>Подсказка:</strong> Эти компоненты не обязательны.
                      Пропустите этот шаг, если они вам не нужны.
                    </p>
                  </div>

                  <form onSubmit={handleStep3Submit} className="space-y-6">
                    <div className="space-y-6">
                      {/* Молдинг */}
                      <div className="wizard-section p-6">
                        <h3 className="text-xl font-semibold text-gray-800 mb-4">
                          Молдинг
                        </h3>
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Выберите молдинг
                            </label>
                            <select
                              value={moldingId}
                              onChange={(e) => {
                                const newMoldingId = e.target.value;
                                setMoldingId(newMoldingId);
                                // Сразу обновляем orderData для пересчета цены
                                updateOrderData({
                                  molding_id: newMoldingId ? parseInt(newMoldingId) : null,
                                  molding_consumption: newMoldingId && moldingConsumption ? parseFloat(moldingConsumption) : null,
                                });
                              }}
                              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                            >
                              <option value="">-- Не выбрано --</option>
                              {moldings.map((molding) => (
                                <option key={molding.id} value={molding.id}>
                                  {molding.name} ({molding.price_per_meter} ₽/м)
                                </option>
                              ))}
                            </select>
                          </div>
                          {moldingId && (
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Расход молдинга (м)
                              </label>
                              <input
                                type="number"
                                step="0.01"
                                min="0"
                                value={moldingConsumption}
                                onChange={(e) => {
                                  const newConsumption = e.target.value;
                                  setMoldingConsumption(newConsumption);
                                  // Сразу обновляем orderData для пересчета цены
                                  if (moldingId && newConsumption) {
                                    updateOrderData({
                                      molding_consumption: parseFloat(newConsumption),
                                    });
                                  }
                                }}
                                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                                placeholder="Расход в метрах"
                              />
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Тросик */}
                      <div className="wizard-section p-6">
                        <h3 className="text-xl font-semibold text-gray-800 mb-4">
                          Тросик
                        </h3>
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Выберите тросик
                            </label>
                            <select
                              value={trosikId}
                              onChange={(e) => {
                                const newTrosikId = e.target.value;
                                setTrosikId(newTrosikId);
                                // Сразу обновляем orderData для пересчета цены
                                updateOrderData({
                                  trosik_id: newTrosikId ? parseInt(newTrosikId) : null,
                                  trosik_length: newTrosikId ? parseFloat(trosikLength || x2 || 0) : null,
                                });
                              }}
                              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                            >
                              <option value="">-- Не выбрано --</option>
                              {trosiki.map((trosik) => (
                                <option key={trosik.id} value={trosik.id}>
                                  {trosik.name} ({trosik.price_per_meter} ₽/м)
                                </option>
                              ))}
                            </select>
                          </div>
                          {trosikId && (
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Длина тросика (м) <span className="text-gray-500 text-xs">(равна ширине картины)</span>
                              </label>
                              <input
                                type="number"
                                step="0.01"
                                min="0"
                                value={trosikLength || x2 || ''}
                                onChange={(e) => setTrosikLength(e.target.value)}
                                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition bg-gray-50"
                                placeholder={x2 ? `Ширина картины: ${x2} м` : 'Введите ширину картины'}
                                readOnly
                              />
                              <p className="mt-1 text-xs text-gray-500">
                                Длина тросика автоматически равна ширине картины ({x2 || 'не указана'} м)
                              </p>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Подвески */}
                      <div className="wizard-section p-6">
                        <h3 className="text-xl font-semibold text-gray-800 mb-4">
                          Подвески
                        </h3>
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Выберите подвески
                            </label>
                            <select
                              value={podveskiId}
                              onChange={(e) => {
                                const newPodveskiId = e.target.value;
                                setPodveskiId(newPodveskiId);
                                // Сразу обновляем orderData для пересчета цены
                                updateOrderData({
                                  podveski_id: newPodveskiId ? parseInt(newPodveskiId) : null,
                                  podveski_quantity: newPodveskiId ? 1 : null,
                                });
                              }}
                              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                            >
                              <option value="">-- Не выбрано --</option>
                              {podveski.map((podveska) => (
                                <option key={podveska.id} value={podveska.id}>
                                  {podveska.name} ({podveska.price_per_unit} ₽/шт)
                                </option>
                              ))}
                            </select>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-between pt-4">
                      <button
                        type="button"
                        onClick={() => setCurrentStep(2)}
                        className="wizard-button-secondary px-8 py-3 font-semibold"
                      >
                        ← Назад
                      </button>
                      <button
                        type="submit"
                        className="wizard-button-primary px-8 py-3 font-semibold"
                      >
                        Далее →
                      </button>
                    </div>
                  </form>
                </>
              )}

              {/* Шаг 4: Фурнитура и упаковка */}
              {currentStep === 4 && (
                <>
                  <h2 className="text-3xl font-bold text-gray-800 mb-6">
                    🔧 Шаг 4: Выберите фурнитуру и упаковку
                  </h2>

                  <form onSubmit={handleStep4Submit} className="space-y-6">
                    <div className="space-y-6">
                      {/* Фурнитура */}
                      <div className="wizard-section p-6">
                        <h3 className="text-xl font-semibold text-gray-800 mb-4">
                          Фурнитура{' '}
                          <span className="text-sm font-normal text-gray-500">
                            (опционально)
                          </span>
                        </h3>
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Выберите фурнитуру
                            </label>
                            <select
                              value={hardwareId}
                              onChange={(e) => {
                                const newHardwareId = e.target.value;
                                setHardwareId(newHardwareId);
                                // Сразу обновляем orderData для пересчета цены
                                updateOrderData({
                                  hardware_id: newHardwareId ? parseInt(newHardwareId) : null,
                                  hardware_quantity: newHardwareId ? hardwareQuantity : 1,
                                });
                              }}
                              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                            >
                              <option value="">-- Не выбрано --</option>
                              {hardware.map((hw) => (
                                <option key={hw.id} value={hw.id}>
                                  {hw.name} ({hw.price_per_unit} ₽/шт)
                                </option>
                              ))}
                            </select>
                          </div>
                          {hardwareId && (
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Количество фурнитуры
                              </label>
                              <input
                                type="number"
                                min="1"
                                value={hardwareQuantity}
                                onChange={(e) => {
                                  const newQuantity = parseInt(e.target.value) || 1;
                                  setHardwareQuantity(newQuantity);
                                  // Сразу обновляем orderData для пересчета цены
                                  if (hardwareId) {
                                    updateOrderData({
                                      hardware_quantity: newQuantity,
                                    });
                                  }
                                }}
                                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                              />
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Упаковка */}
                      <div className="wizard-section p-6">
                        <h3 className="text-xl font-semibold text-gray-800 mb-4">
                          Упаковка{' '}
                          <span className="text-sm font-normal text-gray-500">
                            (опционально)
                          </span>
                        </h3>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Выберите упаковку
                          </label>
                          <select
                            value={packageId}
                            onChange={(e) => {
                              const newPackageId = e.target.value;
                              setPackageId(newPackageId);
                              // Сразу обновляем orderData для пересчета цены
                              updateOrderData({
                                package_id: newPackageId ? parseInt(newPackageId) : null,
                              });
                            }}
                            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                          >
                            <option value="">-- Не выбрано --</option>
                            {packages.map((pkg) => (
                              <option key={pkg.id} value={pkg.id}>
                                {pkg.name} ({pkg.price} ₽)
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-between pt-4">
                      <button
                        type="button"
                        onClick={() => setCurrentStep(3)}
                        className="wizard-button-secondary px-8 py-3 font-semibold"
                      >
                        ← Назад
                      </button>
                      <button
                        type="submit"
                        className="wizard-button-primary px-8 py-3 font-semibold"
                      >
                        Далее →
                      </button>
                    </div>
                  </form>
                </>
              )}

              {/* Шаг 5: Данные клиента */}
              {currentStep === 5 && (
                <>
                  <h2 className="text-3xl font-bold text-gray-800 mb-6">
                    👤 Шаг 5: Данные клиента
                  </h2>
                  <form onSubmit={handleStep5Submit} className="space-y-6">
                    <div className="space-y-6">
                      {/* Имя клиента */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Имя клиента <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={customerName}
                          onChange={(e) => {
                            setCustomerName(e.target.value);
                            setErrors({ ...errors, customer_name: null });
                          }}
                          className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-blue-200 transition ${
                            errors.customer_name
                              ? 'border-red-500'
                              : 'border-gray-300 focus:border-blue-500'
                          }`}
                          placeholder="Введите имя клиента"
                          required
                        />
                        {errors.customer_name && (
                          <p className="mt-1 text-sm text-red-500">{errors.customer_name}</p>
                        )}
                      </div>

                      {/* Телефон клиента */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Телефон клиента <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="tel"
                          value={customerPhone}
                          onChange={(e) => {
                            setCustomerPhone(e.target.value);
                            setErrors({ ...errors, customer_phone: null });
                          }}
                          className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-blue-200 transition ${
                            errors.customer_phone
                              ? 'border-red-500'
                              : 'border-gray-300 focus:border-blue-500'
                          }`}
                          placeholder="+7 (900) 123-45-67"
                          required
                        />
                        {errors.customer_phone && (
                          <p className="mt-1 text-sm text-red-500">{errors.customer_phone}</p>
                        )}
                      </div>

                      {/* Способ оплаты */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Способ оплаты
                        </label>
                        <select
                          value={paymentMethod}
                          onChange={(e) => setPaymentMethod(e.target.value)}
                          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                        >
                          <option value="наличные">Наличные</option>
                          <option value="карта">Банковская карта</option>
                          <option value="перевод">Банковский перевод</option>
                        </select>
                      </div>

                      {/* Аванс */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Аванс (руб) <span className="text-gray-500 text-xs">(опционально)</span>
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          value={advancePayment}
                          onChange={(e) => setAdvancePayment(e.target.value)}
                          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
                          placeholder="0.00"
                        />
                        {priceCalculation?.total_price && (
                          <p className="mt-2 text-sm text-gray-600">
                            Итоговая сумма: <strong>{priceCalculation.total_price.toFixed(2)} ₽</strong>
                            {advancePayment && parseFloat(advancePayment) > 0 && (
                              <span className="ml-2">
                                (Долг: <strong>{(priceCalculation.total_price - parseFloat(advancePayment)).toFixed(2)} ₽</strong>)
                              </span>
                            )}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex justify-between pt-4">
                      <button
                        type="button"
                        onClick={() => setCurrentStep(4)}
                        className="wizard-button-secondary px-8 py-3 font-semibold"
                      >
                        ← Назад
                      </button>
                      <button
                        type="submit"
                        className="wizard-button-primary px-8 py-3 font-semibold"
                      >
                        К итогам →
                      </button>
                    </div>
                  </form>
                </>
              )}
            </div>
          </div>

          <div className="lg:col-span-1">
            <PricePanel />
          </div>
        </div>
      </div>
    </div>
  );
};
