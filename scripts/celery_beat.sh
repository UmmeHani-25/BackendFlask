#!/bin/sh

sleep 20

celery -A app.tasks.celery_app.celery beat --loglevel=info
