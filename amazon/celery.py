from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amazon.settings")

app = Celery('amazon')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = f"amqp://guest@{settings.AMQP_HOST}:5672//"
app.conf.result_backend = settings.CELERY_RESULT_BACKEND
app.conf.result_persistent = False

app.autodiscover_tasks()
