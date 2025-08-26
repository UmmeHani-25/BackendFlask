from app.config import settings
import json
import asyncio
import urllib.parse
import logging
import httpx
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from app.models.db import SessionLocal
from app.models.cars import Make, CarModel, Car
from app.tasks.celery_app import celery

logger = logging.getLogger(__name__)


@celery.task(name="sync_car_data")
def sync_car_data_task():
    asyncio.run(sync_car_data())


async def sync_car_data():
    async with SessionLocal() as session:  
        try:
            where = urllib.parse.quote_plus(
                json.dumps({"Year": {"$gte": 2012, "$lte": 2022}})
            )
            url = (
                "https://parseapi.back4app.com/classes/Car_Model_List"
                f"?limit=5000&order=Year&where={where}"
            )
            headers = {
                "X-Parse-Application-Id": settings.BACK4APP_APP_ID,
                "X-Parse-Master-Key": settings.BACK4APP_MASTER_KEY,
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.get(url, headers=headers)
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

                # --- Make ---
                result = await session.execute(
                    select(Make).where(Make.name == make_name)
                )
                make = result.scalars().first()
                if not make:
                    make = Make(name=make_name)
                    session.add(make)
                    await session.flush()

                # --- Model ---
                result = await session.execute(
                    select(CarModel).where(
                        CarModel.name == model_name,
                        CarModel.make_id == make.id
                    )
                )
                model = result.scalars().first()
                if not model:
                    model = CarModel(name=model_name, make_id=make.id)
                    session.add(model)
                    await session.flush()

                # --- Car ---
                result = await session.execute(
                    select(Car).where(
                        Car.make_id == make.id,
                        Car.model_id == model.id,
                        Car.year == year
                    )
                )
                car = result.scalars().first()
                if not car:
                    car = Car(
                        make_id=make.id,
                        model_id=model.id,
                        year=year,
                        category=category
                    )
                    session.add(car)
                    imported_count += 1

            await session.commit()
            logger.info("Imported %s new car records.", imported_count)

        except (httpx.RequestError, SQLAlchemyError, Exception) as e:
            await session.rollback()
            logger.error("Error in sync_car_data: %s", e)
