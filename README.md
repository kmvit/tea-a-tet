# Тет-а-Тет

React-приложение для багетной мастерской (заказы рамок, расчёт стоимости).

## Требования

- **Python 3.11+** — backend (Django)
- **Node.js 18+** и **npm** — frontend (Vite + React)

---

## Быстрый старт

### 1. Подготовка backend (из корня проекта)

```bash
cd tet-a-tet   # или полный путь к проекту

# Виртуальное окружение
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Зависимости
pip install -r requirements.txt

# Миграции
python manage.py migrate

# Суперпользователь (опционально, для админки)
python manage.py createsuperuser
```

### 2. Установка frontend

```bash
cd frontend
npm install
```

### 3. Запуск

**Терминал 1 — Django:**
```bash
cd tet-a-tet   # корень проекта
source venv/bin/activate
python manage.py runserver
```
→ Backend: http://127.0.0.1:8000

**Терминал 2 — React:**
```bash
cd frontend
npm run dev
```
→ Frontend: http://localhost:3000

Откройте **http://localhost:3000** — запросы к API проксируются на Django.

---

## Полезные команды

| Команда | Описание |
|--------|----------|
| `npm run dev` | Dev-сервер с HMR |
| `npm run build` | Сборка для продакшена |
| `npm run preview` | Просмотр production-сборки |
| `npm run lint` | Проверка ESLint |

---

## Архитектура

- **Backend**: Django REST API на порту 8000
- **Frontend**: React (Vite) на порту 3000
- **Прокси**: запросы `/api/*` перенаправляются на Django

---

## API (кратко)

- `GET /api/baguettes/` — багеты
- `GET /api/glasses/`, `/api/backings/`, `/api/podramniki/` — стекло, подкладка, подрамник
- `GET /api/hardware/`, `/api/packages/` — фурнитура, упаковка
- `GET /api/moldings/`, `/api/trosiki/`, `/api/podveski/` — молдинг, тросик, подвески
- `POST /api/calculate-price/` — расчёт цены
- `POST /api/create-order/` — создание заказа
