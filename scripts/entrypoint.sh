#!/bin/sh
set -e

echo "Applying DB migrations..."
alembic upgrade head

echo "Checking if DB is empty..."
if ! mysql -hmysql -uroot -p1234 fastcar -e "SELECT 1 FROM cars LIMIT 1;" >/dev/null 2>&1; then
    echo "Running initial car data sync..."
    python -c "
from app.tasks.tasks import sync_car_data_task
sync_car_data_task.delay()
print('Initial sync completed')
"
else
    echo "DB already has car data, skipping sync."
fi

echo "Starting FastAPI..."
uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload
