import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.cars import Car
from app.models.db import get_db
from app.web.cars.schemas import CarCreate, CarUpdate, CarOut, QueryRequest, QueryResponse
from app.web.common.jwt import get_current_user
from app.web.common.utils import paginate, get_ids
from app.agents.agent import Neo4jAgent


logger = logging.getLogger(__name__)

router = APIRouter()


# Create car
@router.post("/", response_model=CarOut)
async def create_car(
    car: CarCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    # Get make_id and model_id
    make_id, model_id = await get_ids(db, car.make, car.model)

    # Create car
    db_car = Car(
        make_id=make_id,
        model_id=model_id,
        year=car.year,
        category=car.category
    )
    db.add(db_car)
    await db.commit()
    await db.refresh(db_car)
    return db_car

# Read cars with pagination
@router.get("/", response_model=dict)
async def list_cars(
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),  
):
    query = select(Car)
    items, pagination = await paginate(db, query, page, limit)

    return {
        "items": [CarOut.from_orm(car) for car in items],
        "pagination": pagination,
    }


# Get single car
@router.get("/{car_id}", response_model=CarOut)
async def get_car(
    car_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(Car).where(Car.id == car_id))
    db_car = result.scalars().first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_car


# Update car (PUT/PATCH)
@router.put("/{car_id}", response_model=CarOut)
@router.patch("/{car_id}", response_model=CarOut)
async def update_car(
    car_id: int,
    car_update: CarUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(Car).where(Car.id == car_id))
    db_car = result.scalars().first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")

    # Handle make/model if provided
    if car_update.make and car_update.model:
        db_car.make_id, db_car.model_id = await get_ids(db, car_update.make, car_update.model)

    # Handle other fields
    if car_update.year is not None:
        db_car.year = car_update.year
    if car_update.category is not None:
        db_car.category = car_update.category

    await db.commit()
    await db.refresh(db_car)
    return db_car


# Delete car
@router.delete("/{car_id}")
async def delete_car(
    car_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(Car).where(Car.id == car_id))
    db_car = result.scalars().first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")

    await db.delete(db_car)
    await db.commit()
    return {"detail": "Car deleted"}


# Agent Endpoint
@router.post("/agent/query", response_model=QueryResponse)
async def agent_query(
    query_request: QueryRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    agent = Neo4jAgent()
    response = await agent.agent_pipeline(query_request.query)
    return QueryResponse(response=response)
