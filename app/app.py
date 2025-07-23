import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from app.models.db import db
from app.models import User, Make, Model, Car  # Import models for proper registration
from app.web.common.common import register_blueprints
from app.tasks.celery_app import init_celery

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Core configuration
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///cars.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'dev-secret-key'),
        JWT_TOKEN_LOCATION=["headers"],
        JWT_ACCESS_TOKEN_EXPIRES=False  # or set to timedelta for expiration
    )

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    CORS(app)
    jwt = JWTManager(app)

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'message': 'Token has expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'message': 'Invalid token'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'message': 'Authorization token is required'}), 401

    # Global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'message': 'Bad request'}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'message': 'Internal server error'}), 500

    # Register blueprints
    register_blueprints(app)

    # Initialize Celery
    init_celery(app)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)