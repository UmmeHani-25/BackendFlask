from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.db import db
from app.models.cars import Car
from app.web.cars.schemas import CarCreateSchema, CarUpdateSchema

from app.web.common.utils import (
    serialize_car,
    validate_make_model,
    paginate,
    db_transaction,
    load_json
)

cars_bp = Blueprint('cars', __name__)

@cars_bp.route('/', methods=['GET'])
def get_cars():
    paginated = paginate(Car.query)
    return jsonify([serialize_car(car) for car in paginated.items]), 200

@cars_bp.route('/<int:car_id>', methods=['GET'])
def get_car(car_id):
    car = Car.query.get_or_404(car_id)
    return jsonify(serialize_car(car)), 200

@cars_bp.route('/', methods=['POST'])
@jwt_required()
@db_transaction
def create_car():
    data, errors = load_json(CarCreateSchema())
    if errors:
        return jsonify({'message': 'Validation error', 'errors': errors}), 400

    if not validate_make_model(data['make_id'], data['model_id']):
        return jsonify({'message': 'Invalid make_id or model_id combination'}), 400

    car = Car(**data)
    db.session.add(car)
    db.session.commit()
    return jsonify(serialize_car(car)), 201

@cars_bp.route('/<int:car_id>', methods=['PUT'])
@jwt_required()
@db_transaction
def update_car(car_id):
    car = Car.query.get_or_404(car_id)
    data, errors = load_json(CarUpdateSchema(), partial=True)
    if errors:
        return jsonify({'message': 'Validation error', 'errors': errors}), 400

    if 'make_id' in data or 'model_id' in data:
        make_id = data.get('make_id', car.make_id)
        model_id = data.get('model_id', car.model_id)
        if not validate_make_model(make_id, model_id):
            return jsonify({'message': 'Invalid make_id or model_id combination'}), 400

    for key, val in data.items():
        setattr(car, key, val)

    db.session.commit()
    return jsonify(serialize_car(car)), 200

@cars_bp.route('/<int:car_id>', methods=['DELETE'])
@jwt_required()
@db_transaction
def delete_car(car_id):
    car = Car.query.get_or_404(car_id)
    result = serialize_car(car)
    db.session.delete(car)
    db.session.commit()
    return jsonify({'message': 'Car deleted successfully', 'deleted': result}), 200
