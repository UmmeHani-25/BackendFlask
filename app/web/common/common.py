from fastapi import FastAPI
from app.web.users.api import router as users_bp
from app.web.cars.api import router as cars_bp


def register_routers(app: FastAPI):
    app.include_router(users_bp, prefix="/users", tags=["users"])
    app.include_router(cars_bp, prefix="/cars", tags=["cars"])
