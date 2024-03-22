import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'img_finder.settings')

app = Celery('img_finder')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'every-day': {
        'task': 'img_app.tasks.periodic_image_search',
        'schedule': crontab(minute="0", hour="0"),
    },
}
