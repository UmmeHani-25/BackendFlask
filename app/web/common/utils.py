from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from app.models.db import db

def paginate(query):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('limit', 20))
    return query.paginate(page=page, per_page=per_page, error_out=False)

def load_json(schema, partial=False):
    try:
        return schema.load(request.get_json() or {}, partial=partial), None
    except ValidationError as e:
        return None, e.messages

def db_transaction(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({'message': 'Database error occurred'}), 500
    return wrapper

def serialize_car(car):
    return {
        'id': car.id,
        'make_id': car.make_id,
        'model_id': car.model_id,
        'make': car.make.name if car.make else None,
        'model': car.model.name if car.model else None,
        'year': car.year,
        'category': car.category
    }

def validate_make_model(make_id, model_id):
    from app.models.cars import Make, CarModel
    make = Make.query.get(make_id)
    model = CarModel.query.get(model_id)
    return make and model and model.make_id == make.id
