import os
from celery import Celery
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

celery = Celery(
    'app',
    broker=os.getenv('CELERY_BROKER_URL'),
    backend=os.getenv('CELERY_RESULT_BACKEND'),
    include=['app.tasks']
)


celery.conf.beat_schedule = {
    'sync_car_data': {
        'task': 'sync_car_data',
        'schedule': timedelta(minutes=10),  
    },  
}

celery.conf.timezone = 'UTC'
