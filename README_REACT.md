# Миграция на React Frontend

Проект был успешно мигрирован на React. Теперь фронтенд работает как отдельное SPA приложение.

## Структура проекта

- `frontend/` - React приложение (Vite + React Router)
- `frames/api_views.py` - API endpoints для React
- `config/settings.py` - Настройки CORS для работы с React

## Установка и запуск

### 1. Установка зависимостей Django

```bash
pip install -r requirements.txt
```

### 2. Установка зависимостей React

```bash
cd frontend
npm install
```

Если возникают проблемы с сетью, можно установить пакеты вручную:
- react-router-dom
- axios

### 3. Запуск Django сервера

```bash
python manage.py runserver
```

Сервер будет доступен на `http://127.0.0.1:8000`

### 4. Запуск React приложения

В отдельном терминале:

```bash
cd frontend
npm run dev
```

React приложение будет доступно на `http://localhost:3000`

## API Endpoints

Все API endpoints доступны по адресу `http://127.0.0.1:8000/api/`:

- `GET /api/baguettes/` - Список багетов
- `GET /api/glasses/` - Список стекол
- `GET /api/backings/` - Список подкладок
- `GET /api/hardware/` - Список фурнитуры
- `GET /api/podramniki/` - Список подрамников
- `GET /api/packages/` - Список упаковок
- `GET /api/moldings/` - Список молдингов
- `GET /api/trosiki/` - Список тросиков
- `GET /api/podveski/` - Список подвесок
- `POST /api/calculate-price/` - Расчет цены
- `POST /api/create-order/` - Создание заказа

## Особенности реализации

1. **Управление состоянием**: Используется React Context API для хранения данных заказа
2. **Маршрутизация**: React Router для навигации между шагами
3. **API интеграция**: Axios для запросов к Django backend
4. **Стилизация**: Tailwind CSS через CDN
5. **Расчет цены**: Автоматический расчет при изменении данных заказа

## Следующие шаги

Для продакшена рекомендуется:
1. Настроить сборку React приложения (`npm run build`)
2. Настроить Django для раздачи статических файлов React
3. Настроить прокси для API запросов или использовать абсолютные URL
4. Установить Tailwind CSS через npm вместо CDN
