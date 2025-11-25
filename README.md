# Система комментариев

Полнофункциональное веб-приложение для управления комментариями с поддержкой вложенных ответов, загрузки файлов, форматирования текста и real-time уведомлений через WebSocket.

## Технологии

**Backend:**
- Django 5.2 + Django REST Framework
- PostgreSQL (база данных)
- Redis (кэш и брокер сообщений)
- Celery (фоновые задачи)
- Django Channels (WebSocket)
- Cloudinary (хранение файлов)

**Frontend:**
- Vue.js 3 + TypeScript
- Pinia (управление состоянием)
- TipTap (rich text редактор)
- Tailwind CSS
- Vue Router

## Быстрый старт

### Требования
- Docker и Docker Compose

### Запуск приложения

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd dZENcode-Test-Task
   ```

2. **Создайте файл `.env` в корневой директории** со следующими переменными:
   ```env
   # Django
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database
   DB_NAME=comments_db
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=postgres
   DB_PORT=5432
   
   # Cloudinary
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   
   # ReCaptcha
   RECAPTCHA_PUBLIC_KEY=your-public-key
   RECAPTCHA_PRIVATE_KEY=your-private-key
   VITE_RECAPTCHA_SITE_KEY=your-site-key
   
   # Frontend
   VITE_API_BASE_URL=http://localhost:8000
   VITE_API_HOST=localhost:8000
   ```

3. **Запустите приложение:**
   ```bash
   docker-compose up --build
   ```

4. **Откройте браузер:**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API документация: http://localhost:8000/api/schema/swagger-ui/

### Создание суперпользователя

```bash
docker exec -it comments_backend python manage.py createsuperuser
```

## Основные функции

### 💬 Комментарии
- Создание комментариев с rich text форматированием (жирный, курсив, код, ссылки)
- Вложенные ответы (неограниченная глубина)
- Предпросмотр HTML в реальном времени
- Защита от XSS (санитизация HTML)

### 📎 Вложения
- Загрузка изображений (JPG, PNG, GIF) до 320x240
- Загрузка текстовых файлов (TXT) до 100KB
- Хранение в Cloudinary

### 🔍 Фильтрация и сортировка
- Фильтр по имени пользователя
- Фильтр по email
- Сортировка по дате (новые/старые)
- Пагинация (25 комментариев на страницу)

### 🔔 Real-time уведомления
- WebSocket соединение для мгновенных уведомлений
- Уведомления о новых ответах на комментарии
- JWT аутентификация для WebSocket

### 🔐 Безопасность
- JWT аутентификация
- Google ReCaptcha v2 для создания комментариев
- CORS настройки
- Валидация файлов

### 👤 Пользователи
- Регистрация и вход
- Профиль пользователя
- Управление своими комментариями

## Структура проекта

```
dZENcode-Test-Task/
├── app/                    # Django приложение (комментарии)
├── comments_api/           # Django проект (настройки)
├── vue_ui/                 # Vue.js frontend
├── docker-compose.yml      # Docker конфигурация
├── Dockerfile              # Backend Dockerfile
└── README.md
```

## API Endpoints

- `POST /api/register/` - Регистрация
- `POST /api/login/` - Вход
- `GET /api/comments/` - Список комментариев
- `POST /api/comments/` - Создать комментарий
- `GET /api/comments/{id}/` - Детали комментария
- `WS /ws/notifications/` - WebSocket уведомления

Полная документация API доступна по адресу: http://localhost:8000/api/schema/swagger-ui/

## Разработка

### Локальный запуск без Docker

**Backend:**
```bash
# Установка зависимостей
uv sync

# Миграции
uv run manage.py migrate

# Запуск сервера
uv run uvicorn comments_api.asgi:application --host 0.0.0.0 --port 8000

# Celery worker
uv run celery -A comments_api worker -l info

# Celery beat
uv run celery -A comments_api beat -l info
```

**Frontend:**
```bash
cd vue_ui
npm install
npm run dev
```

## Лицензия

MIT License