import os
import json
import urllib.parse
import requests
from app.app import create_app
from app.models.cars import Make, CarModel, Car
from app.models.db import db
from app.tasks.celery_app import celery


app = create_app()

@celery.task
def sync_car_data():
    with app.app_context():
        where = urllib.parse.quote_plus(json.dumps({
            "Year": {"$gte": 2012, "$lte": 2022}
        }))
        url = (
            f'https://parseapi.back4app.com/classes/Car_Model_List'
            f'?limit=5000&order=Year&where={where}'
        )
        headers = {
            'X-Parse-Application-Id': 'hlhoNKjOvEhqzcVAJ1lxjicJLZNVv36GdbboZj3Z',
            'X-Parse-Master-Key': 'SNMJJF0CZZhTPhLDIqGhTlUNV9r60M2Z5spyWfXW'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f'Request failed with status code {response.status_code}')
            return

        results = response.json().get('results', [])
        for result in results:
            make_name = result.get('Make')
            model_name = result.get('Model')
            year = result.get('Year')
            category = result.get('Category')

            if not all([make_name, model_name, year]):
                continue

            # Add Make
            make = Make.query.filter_by(name=make_name).first()
            if not make:
                make = Make(name=make_name)
                db.session.add(make)
                db.session.commit()

            # Add Model
            car_model = CarModel.query.filter_by(name=model_name, make_id=make.id).first()
            if not car_model:
                car_model = CarModel(name=model_name, make_id=make.id)
                db.session.add(car_model)
                db.session.commit()

            # Add Car
            car = Car.query.filter_by(make_id=make.id, model_id=car_model.id, year=year).first()
            if not car:
                car = Car(make_id=make.id, model_id=car_model.id, year=year, category=category or "")
                db.session.add(car)
                db.session.commit()

        print(f"Imported {len(results)} car records.")

if __name__ == '__main__':
    sync_car_data()
