#!/bin/sh

sleep 10

if [ ! -d "migrations" ]; then
    flask db init
fi

flask db migrate -m "Initial migration" || true

flask db upgrade

python -c "from app.tasks.tasks import sync_car_data; sync_car_data()"

flask run --host=0.0.0.0


