import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    # API configuration
    API_TITLE: str = "FastAPI Car Registration"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "A simple FastAPI project with MySQL"

    # Database configuration
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    
    # JWT configuration
    JWT_SECRET: str = os.getenv('JWT_SECRET_KEY')
  
    # Celery configuration
    CELERY_BROKER_URL: str = os.getenv('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND: str = os.getenv('CELERY_RESULT_BACKEND')

    #  BACK4API CONFIGURATIONS
    BACK4APP_APP_ID: str = os.getenv("BACK4APP_APP_ID")
    BACK4APP_MASTER_KEY: str = os.getenv("BACK4APP_MASTER_KEY")

    # Neo4j
    NEO4J_URI: str = os.getenv("NEO4J_URI")
    NEO4J_USER: str = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
