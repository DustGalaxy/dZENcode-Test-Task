import logging
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "comments_api.settings")

from celery import Celery
from celery.signals import after_setup_logger

from comments_api.celery_settings import CELERY


logger = logging.getLogger(__name__)

app = Celery("comments_api")

app.config_from_object(CELERY)

app.autodiscover_tasks()


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh = logging.FileHandler("logs.log")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
