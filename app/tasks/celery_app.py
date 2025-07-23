import os
from celery import Celery

celery = Celery(
    __name__,
    broker=os.getenv('CELERY_BROKER_URL'),
    backend=os.getenv('CELERY_RESULT_BACKEND'),
    include=['app.tasks.tasks'],  # Register your task module
)

# Schedule the sync every 10 minutes
celery.conf.beat_schedule = {
    'sync-car-data-every-10-minutes': {
        'task': 'app.tasks.tasks.sync_car_data',
        'schedule': 600.0,
    }
}

def init_celery(app):
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
