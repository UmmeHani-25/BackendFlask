# app/tasks/tasks.py

import json
import urllib.parse
import requests
from app.tasks.celery_app import celery
from app.models.db import db
from app.models.cars import Make, Model, Car

@celery.task(name='app.tasks.tasks.sync_car_data')
def sync_car_data():
    try:
        # 1) Prepare the Back4App query
        where = urllib.parse.quote_plus(json.dumps({
            "Year": {"$gte": 2012, "$lte": 2022}
        }))
        url = (
            f'https://parseapi.back4app.com/classes/Car_Model_List'
            f'?limit=5000&order=Year&where={where}'
        )
        headers = {
            'X-Parse-Application-Id': 'hlhoNKjOvEhqzcVAJ1lxjicJLZNVv36GdbboZj3Z',
            'X-Parse-Master-Key':       'SNMJJF0CZZhTPhLDIqGhTlUNV9r60M2Z5spyWfXW'
        }

        # 2) Fetch and parse JSON
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch: HTTP {response.status_code}")
            return "API request failed"

        data = response.json().get("results", [])
        if not data:
            print("Back4App returned no records.")
            return "No data received from API"

        # 3) Show a sample for debugging
        print("Sample data received:")
        print(json.dumps(data[:3], indent=2))

        count = 0
        for item in data:
            make_name  = item.get("Make")
            model_name = item.get("Model")
            year       = item.get("Year")
            category   = item.get("Category")

            if not (make_name and model_name and year):
                continue

            # 4) Get or create Make
            make = Make.query.filter_by(name=make_name).first()
            if not make:
                make = Make(name=make_name)
                db.session.add(make)
                db.session.flush()       # populates make.id

            # 5) Get or create Model (linked to Make)
            model = Model.query.filter_by(
                name=model_name,
                make_id=make.id
            ).first()
            if not model:
                model = Model(name=model_name, make_id=make.id)
                db.session.add(model)
                db.session.flush()      # populates model.id

            # 6) Avoid inserting duplicates
            exists = Car.query.filter_by(
                make_id=make.id,
                model_id=model.id,
                year=year
            ).first()
            if exists:
                continue

            # 7) Create the Car record
            car = Car(
                make_id=make.id,
                model_id=model.id,
                year=year,
                category=category
            )
            db.session.add(car)
            count += 1

        # 8) Commit everything in one go
        db.session.commit()
        print(f"Sync complete. Added {count} new cars.")
        return f"Sync complete. Added {count} new cars."

    except Exception as e:
        # Catch-all to prevent silent failures
        print("Error during sync:", str(e))
        db.session.rollback()
        return "Sync failed due to exception"
