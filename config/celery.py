import os

import django
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

app = Celery('config')

from django_celery_beat.models import PeriodicTask, IntervalSchedule


app.config_from_object('django.conf:settings', namespace='CELERY')

broker_transport_options = {'max_retries': 3}
app.autodiscover_tasks()