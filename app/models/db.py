from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from app.config import settings


DATABASE_URL = settings.DATABASE_URL

# Async engine for FASTAPI WEB LAYER
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = async_sessionmaker(
    bind = engine,
    class_ = AsyncSession,
    expire_on_commit = False,
)

async def get_db():
    async with SessionLocal() as session:
        yield session
