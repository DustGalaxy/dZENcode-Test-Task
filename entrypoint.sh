#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  sleep 1
done
echo "PostgreSQL is ready!"

echo "Running database migrations..."
uv run manage.py migrate --noinput

echo "Collecting static files..."
uv run manage.py collectstatic --noinput
 
echo "Starting server..."
echo "$1" "$2"
if [ "$2" = "celery_worker" ]; then
    uv run celery -A comments_api worker --loglevel=info
elif [ "$2" = "celery_beat" ]; then
    uv run celery -A comments_api beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
else
    uv run gunicorn comments_api.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
fi
