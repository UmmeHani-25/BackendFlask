#!/bin/sh

echo "Loading MySQL..."
until nc -z mysql 3306; do
  sleep 1
done
echo " MySQL is up"

echo "Loading Redis..."
until nc -z redis 6379; do
  sleep 1
done
echo "Redis is up"

# Run DB migrations
if [ ! -d "migrations" ]; then
    echo "No migrations folder found. Initializing..."
    flask db init
fi

flask db migrate -m "Initial migration" || true
flask db upgrade

# Run initial sync
python -c "from app.tasks.tasks import sync_car_data; sync_car_data()"

# Start Flask
exec flask run --host=0.0.0.0 --port=5000
