import json
import urllib.parse
import requests
import logging
from sqlalchemy.orm import Session

from app.models.cars import Make, CarModel, Car
from app.models.db import SessionLocal
from app.tasks.celery_app import celery

logger = logging.getLogger(__name__)

@celery.task(name="sync_car_data")
def sync_car_data():
    session: Session = SessionLocal()
    try:
        where = urllib.parse.quote_plus(json.dumps({"Year": {"$gte": 2012, "$lte": 2022}}))
        url = (
            "https://parseapi.back4app.com/classes/Car_Model_List"
            f"?limit=5000&order=Year&where={where}"
        )
        headers = {
            "X-Parse-Application-Id": "hlhoNKjOvEhqzcVAJ1lxjicJLZNVv36GdbboZj3Z",
            "X-Parse-Master-Key": "SNMJJF0CZZhTPhLDIqGhTlUNV9r60M2Z5spyWfXW",
        }

        resp = requests.get(url, headers=headers, timeout=60)
        resp.raise_for_status()
        results = resp.json().get("results", [])

        for r in results:
            make_name = r.get("Make")
            model_name = r.get("Model")
            year = r.get("Year")
            category = r.get("Category") or ""

            if not (make_name and model_name and year):
                continue

            make = session.query(Make).filter_by(name=make_name).first()
            if not make:
                make = Make(name=make_name)
                session.add(make)
                session.flush()

            model = (
                session.query(CarModel)
                .filter_by(name=model_name, make_id=make.id)
                .first()
            )
            if not model:
                model = CarModel(name=model_name, make_id=make.id)
                session.add(model)
                session.flush()

            car = (
                session.query(Car)
                .filter_by(make_id=make.id, model_id=model.id, year=year)
                .first()
            )
            if not car:
                car = Car(make_id=make.id, model_id=model.id, year=year, category=category)
                session.add(car)

        session.commit()
        logger.info("Imported %s car records.", len(results))
    except Exception as e:
        session.rollback()
        logger.error("Error in sync_car_data: %s", e)
    finally:
        session.close()
