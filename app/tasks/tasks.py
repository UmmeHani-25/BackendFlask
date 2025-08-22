from app.config import settings
import json
import urllib.parse
import requests
import logging
from sqlalchemy.exc import SQLAlchemyError

from app.models.cars import Make, CarModel, Car
from app.models.db import SyncSessionLocal
from app.tasks.celery_app import celery

logger = logging.getLogger(__name__)

@celery.task(name="sync_car_data")
def sync_car_data():
    session = SyncSessionLocal()
    try:
        where = urllib.parse.quote_plus(json.dumps({"Year": {"$gte": 2012, "$lte": 2022}}))
        url = (
            "https://parseapi.back4app.com/classes/Car_Model_List"
            f"?limit=5000&order=Year&where={where}"
        )
        headers = {
            "X-Parse-Application-Id": settings.BACK4APP_APP_ID,
            "X-Parse-Master-Key": settings.BACK4APP_MASTER_KEY,
        }

        resp = requests.get(url, headers=headers, timeout=60)
        resp.raise_for_status()
        results = resp.json().get("results", [])

        imported_count = 0

        for r in results:
            make_name = r.get("Make")
            model_name = r.get("Model")
            year = r.get("Year")
            category = r.get("Category") or ""

            if not (make_name and model_name and year):
                continue

            # Add Make 
            make = session.query(Make).filter_by(name=make_name).first()
            if not make:
                make = Make(name=make_name)
                session.add(make)
                session.flush()

            # Add Model 
            model = (
                session.query(CarModel)
                .filter_by(name=model_name, make_id=make.id)
                .first()
            )
            if not model:
                model = CarModel(name=model_name, make_id=make.id)
                session.add(model)
                session.flush()

            # Add Car 
            car = (
                session.query(Car)
                .filter_by(make_id=make.id, model_id=model.id, year=year)
                .first()
            )
            if not car:
                car = Car(make_id=make.id, model_id=model.id, year=year, category=category)
                session.add(car)
                imported_count += 1

        session.commit()
        logger.info("Imported %s new car records.", imported_count)

    except (requests.RequestException, SQLAlchemyError, Exception) as e:
        session.rollback()
        logger.error("Error in sync_car_data: %s", e)
    finally:
        session.close()
