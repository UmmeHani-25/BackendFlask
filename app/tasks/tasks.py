import os
import json
import urllib.parse
import requests
import logging

from app.models.cars import Make, CarModel, Car
from app.models.db import SessionLocal  
from app.tasks.celery_app import celery

logger = logging.getLogger(__name__)

@celery.task(name='sync_car_data')
def sync_car_data():
    session = SessionLocal()  
    try:
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
            logger.error(f"Request failed with status code {response.status_code}")
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
            make = session.query(Make).filter_by(name=make_name).first()
            if not make:
                make = Make(name=make_name)
                session.add(make)
                session.flush()  

            # Add Model
            car_model = session.query(CarModel).filter_by(name=model_name, make_id=make.id).first()
            if not car_model:
                car_model = CarModel(name=model_name, make_id=make.id)
                session.add(car_model)
                session.flush()

            # Add Car
            car = session.query(Car).filter_by(
                make_id=make.id,
                model_id=car_model.id,
                year=year
            ).first()
            if not car:
                car = Car(
                    make_id=make.id,
                    model_id=car_model.id,
                    year=year,
                    category=category or ""
                )
                session.add(car)

        session.commit()
        logger.info(f"Imported {len(results)} car records.")

    except Exception as e:
        session.rollback()
        logger.error(f"Error in sync_car_data: {e}")
    finally:
        session.close()
