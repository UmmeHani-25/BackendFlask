from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings


DATABASE_URL = settings.DATABASE_URL

# Async engine for FASTAPI WEB LAYER
engine = create_async_engine(
    DATABASE_URL,
    echo = True,
    future = True,
)

SessionLocal = async_sessionmaker(
    bind = engine,
    class_ = AsyncSession,
    expire_on_commit = False,
)

async def get_db():
    async with SessionLocal() as session:
        yield session


# Sync Engine (Celery Worker)
sync_engine = create_engine(
    DATABASE_URL.replace("+asyncmy", "+pymysql"),  
    echo=True,
    future=True,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False,
)
