from flask import Blueprint

def register_blueprints(app):
    from app.web.users.api import users_bp
    from app.web.cars.api import cars_bp
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(cars_bp, url_prefix='/cars')