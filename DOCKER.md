# Docker Deployment Guide

## Quick Start

1. **Убедитесь, что `.env` файл содержит все необходимые переменные окружения:**

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
PRODUCTION=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=comments_db
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=postgres
DB_PORT=5432

# Redis
CELERY_BROKER_URL=redis://redis:6379/0
REDIS_CACHE_URL=redis://redis:6379/1
REDIS_HOST=redis

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# ReCAPTCHA
RECAPTCHA_PUBLIC_KEY=your-public-key
RECAPTCHA_PRIVATE_KEY=your-private-key
VITE_RECAPTCHA_SITE_KEY=your-public-key

# Frontend
VITE_API_BASE_URL=/api
```

2. **Запустите все сервисы:**

```bash
docker-compose up -d
```

3. **Проверьте статус сервисов:**

```bash
docker-compose ps
```

4. **Откройте приложение в браузере:**

- Frontend: http://localhost
- API Swagger: http://localhost/api/schema/swagger/

## Сервисы

### Backend Services

- **postgres** - PostgreSQL 16 база данных (порт 5432)
- **redis** - Redis кэш и брокер сообщений (порт 6379)
- **backend** - Django приложение с Daphne (порт 8000)
- **celery_worker** - Celery worker для фоновых задач
- **celery_beat** - Celery beat планировщик

### Frontend Service

- **frontend** - Vue.js + Nginx с reverse proxy (порт 80)

## Полезные команды

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f frontend
```

### Выполнение команд Django

```bash
# Создать суперпользователя
docker-compose exec backend python manage.py createsuperuser

# Применить миграции
docker-compose exec backend python manage.py migrate

# Собрать статические файлы
docker-compose exec backend python manage.py collectstatic
```

### Управление сервисами

```bash
# Остановить все сервисы
docker-compose down

# Остановить и удалить volumes (УДАЛИТ ВСЕ ДАННЫЕ!)
docker-compose down -v

# Пересобрать образы
docker-compose build

# Пересобрать и запустить
docker-compose up -d --build

# Перезапустить конкретный сервис
docker-compose restart backend
```

### Доступ к базе данных

```bash
# PostgreSQL shell
docker-compose exec postgres psql -U postgres -d comments_db

# Redis CLI
docker-compose exec redis redis-cli
```

## Архитектура

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│              (Vue.js + Nginx)                    │
│                  Port 80                         │
└────────────┬────────────────────────────────────┘
             │
             │ Reverse Proxy
             │
┌────────────▼────────────────────────────────────┐
│                   Backend                        │
│            (Django + Daphne)                     │
│                  Port 8000                       │
└─────┬──────────────────────────┬────────────────┘
      │                          │
      │                          │
┌─────▼──────────┐      ┌────────▼────────┐
│   PostgreSQL   │      │      Redis      │
│    Port 5432   │      │    Port 6379    │
└────────────────┘      └─────────┬───────┘
                                  │
                    ┌─────────────┴──────────────┐
                    │                            │
            ┌───────▼────────┐        ┌─────────▼────────┐
            │ Celery Worker  │        │  Celery Beat     │
            │                │        │  (Scheduler)     │
            └────────────────┘        └──────────────────┘
```

## Troubleshooting

### Backend не запускается

Проверьте логи:
```bash
docker-compose logs backend
```

Убедитесь, что PostgreSQL готов:
```bash
docker-compose exec postgres pg_isready
```

### Frontend показывает ошибки API

Проверьте, что backend запущен:
```bash
docker-compose ps backend
```

Проверьте Nginx конфигурацию:
```bash
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

### Celery worker не обрабатывает задачи

Проверьте подключение к Redis:
```bash
docker-compose exec redis redis-cli ping
```

Проверьте логи worker:
```bash
docker-compose logs celery_worker
```

## Production Considerations

1. **Используйте HTTPS** - настройте SSL сертификаты для Nginx
2. **Измените SECRET_KEY** - используйте криптографически стойкий ключ
3. **Настройте DEBUG=False** - отключите режим отладки
4. **Настройте ALLOWED_HOSTS** - укажите ваш домен
5. **Используйте managed database** - для production лучше использовать managed PostgreSQL
6. **Настройте backup** - регулярное резервное копирование базы данных
7. **Мониторинг** - добавьте мониторинг сервисов (Prometheus, Grafana)
8. **Логирование** - настройте централизованное логирование
