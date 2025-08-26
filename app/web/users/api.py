import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.users import User  
from app.models.db import get_db   
from app.web.common.jwt import create_access_token, create_refresh_token
from app.web.users.schemas import UserCreate, UserLogin, UserResponse, TokenResponse


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # check if user already exists
    result = await db.execute(select(User).where(User.username == user.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail = "Username already taken")

    # create new user
    new_user = User(username=user.username)
    new_user.set_password(user.password)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user.username))
    db_user = result.scalars().first()

    if not db_user or not db_user.check_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # generate tokens
    access_token = create_access_token({"sub": db_user.username})
    refresh_token = create_refresh_token({"sub": db_user.username})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
