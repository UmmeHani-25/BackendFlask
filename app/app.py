from flask import Flask, app
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from app.web.common.common import register_blueprints
from app.config import Config
from app.models.db import db
from app.models.cars import Car
from app.models.users import User
import logging.config
from app.logging_config import LOGGING_CONFIG

load_dotenv()

migrate = Migrate()

logging.config.dictConfig(LOGGING_CONFIG)

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    register_blueprints(app)
      
    return app