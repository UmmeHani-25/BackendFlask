#!/bin/sh

sleep 15

celery -A app.tasks.celery_app.celery worker --loglevel=info 
