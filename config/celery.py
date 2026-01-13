import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

app = Celery('price_action_reviewer')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'sync-daily-data': {
        'task': 'apps.market_data.tasks.sync_daily_data',
        'schedule': crontab(hour=15, minute=30, day_of_week='1-5'),
    },
    'batch-calculate-indicators': {
        'task': 'apps.technical_analysis.tasks.batch_calculate_indicators',
        'schedule': crontab(hour=16, minute=0, day_of_week='1-5'),
    },
    'weekly-pattern-detection': {
        'task': 'apps.technical_analysis.tasks.batch_detect_patterns',
        'schedule': crontab(hour=20, minute=0, day_of_week=0),
    },
}
