import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "relief_campaign_service.settings")
app = Celery("relief_campaign_service")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.broker_url = "redis://redis:6379/0"

app.autodiscover_tasks()
