from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta
from flask_migrate import Migrate
from app.models.db import db
from app.web.common.common import register_blueprints
import os

load_dotenv()

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    expires = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 1800))
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=expires)

    db.init_app(app)
    
    migrate.init_app(app, db)

    JWTManager(app)

    register_blueprints(app)

    from app.web.users import api as users_api
    from app.web.cars import api as cars_api

    from app.models import cars, users

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

    