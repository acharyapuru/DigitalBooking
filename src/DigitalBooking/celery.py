import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DigitalBooking.settings')

app = Celery('DigitalBooking')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

