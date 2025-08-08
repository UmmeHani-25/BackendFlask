from flask_smorest import Api
from app.web.users.api import users_bp
from app.web.cars.api import cars_bp

def register_blueprints(app):
    api = Api(app)
    api.register_blueprint(users_bp, url_prefix="/users")
    api.register_blueprint(cars_bp, url_prefix="/cars")
