from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.cars import Make, CarModel


async def paginate(
    db: AsyncSession, 
    query, 
    page: int = 1, 
    limit: int = 10
):
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    items_result = await db.execute(
        query.offset((page - 1) * limit).limit(limit)
    )
    items = items_result.scalars().all()

    return items, {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total // limit) + (1 if total % limit else 0),
    }


async def get_ids(db: AsyncSession, make_name: str, model_name: str):
    # Lookup make
    result = await db.execute(select(Make).where(Make.name == make_name))
    make_obj = result.scalar_one_or_none()
    if not make_obj:
        raise HTTPException(status_code=400, detail=f"Make '{make_name}' does not exist.")

    # Lookup model under this make
    result = await db.execute(
        select(CarModel).where(CarModel.name == model_name, CarModel.make_id == make_obj.id)
    )
    model_obj = result.scalar_one_or_none()
    if not model_obj:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_name}' for make '{make_name}' does not exist."
        )

    return make_obj.id, model_obj.id
