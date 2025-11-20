from django.conf import settings

CELERY = {
    "broker_url": settings.CELERY_BROKER_URL,
    "timezone": settings.TIME_ZONE,
    "result_extended": True,
    "beat_scheduler": settings.CELERY_BEAT_SCHEDULER,
    "result_backend": settings.CELERY_RESULT_BACKEND,
}
