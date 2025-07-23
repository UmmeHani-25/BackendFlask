from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.models.db import db
from app.models.cars import Make, Model, Car
from app.web.cars.schemas import CarSchema, CarCreateSchema, CarUpdateSchema
from app.web.common.utils import paginate

cars_bp = Blueprint('cars', __name__)

@cars_bp.route('', methods=['GET'])
@jwt_required()
def list_cars():
    try:
        # explicit join conditions added below
        query = db.session.query(
            Car,
            Make.name.label('make'),
            Model.name.label('model')
        ).join(Make, Car.make_id == Make.id
        ).join(Model, Car.model_id == Model.id)

        # Apply filters
        if 'make' in request.args:
            query = query.filter(Make.name.ilike(f"%{request.args['make']}%"))
        if 'model' in request.args:
            query = query.filter(Model.name.ilike(f"%{request.args['model']}%"))
        if 'year' in request.args:
            try:
                year = int(request.args['year'])
                query = query.filter(Car.year == year)
            except ValueError:
                return jsonify({'message': 'Invalid year parameter'}), 400

        page_obj = paginate(query)
        items = []
        for car, make_name, model_name in page_obj.items:
            data = {
                'id': car.id,
                'make_id': car.make_id,
                'model_id': car.model_id,
                'make': make_name,
                'model': model_name,
                'year': car.year,
                'category': car.category
            }
            items.append(data)

        return jsonify({
            'total': page_obj.total,
            'page': page_obj.page,
            'pages': page_obj.pages,
            'items': items
        }), 200
        
    except Exception as e:
        print("Error in list_cars:", e)
        return jsonify({'message': 'Failed to retrieve cars'}), 500


@cars_bp.route('', methods=['POST'])
@jwt_required()
def create_car():
    try:
        data = CarCreateSchema().load(request.json or {})
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400

    try:
        make = Make.query.get(data['make_id'])
        model = Model.query.filter_by(id=data['model_id'], make_id=data['make_id']).first()
        
        if not make:
            return jsonify({'message': 'Make not found'}), 404
        if not model:
            return jsonify({'message': 'Model not found or does not belong to the specified make'}), 404

        existing = Car.query.filter_by(
            make_id=data['make_id'],
            model_id=data['model_id'],
            year=data['year'],
            category=data.get('category')
        ).first()
        
        if existing:
            return jsonify({'message': 'Car with these specifications already exists'}), 409

        car = Car(**data)
        db.session.add(car)
        db.session.commit()

        result = CarSchema().dump({
            'id': car.id,
            'make_id': car.make_id,
            'model_id': car.model_id,
            'make': make.name,
            'model': model.name,
            'year': car.year,
            'category': car.category
        })
        return jsonify(result), 201
        
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'message': 'Database error occurred'}), 500


@cars_bp.route('/<int:car_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_car(car_id):
    try:
        car = Car.query.get_or_404(car_id)
        schema = CarUpdateSchema(partial=(request.method == 'PATCH'))
        data = schema.load(request.json or {})
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400

    try:
        if 'make_id' in data or 'model_id' in data:
            make_id = data.get('make_id', car.make_id)
            model_id = data.get('model_id', car.model_id)
            
            make = Make.query.get(make_id)
            model = Model.query.filter_by(id=model_id, make_id=make_id).first()
            
            if not make:
                return jsonify({'message': 'Make not found'}), 404
            if not model:
                return jsonify({'message': 'Model not found or does not belong to the specified make'}), 404

        for key, val in data.items():
            setattr(car, key, val)
        
        db.session.commit()

        make_name = car.make.name
        model_name = car.model.name
        
        result = CarSchema().dump({
            'id': car.id,
            'make_id': car.make_id,
            'model_id': car.model_id,
            'make': make_name,
            'model': model_name,
            'year': car.year,
            'category': car.category
        })
        return jsonify(result), 200
        
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'message': 'Database error occurred'}), 500


@cars_bp.route('/<int:car_id>', methods=['DELETE'])
@jwt_required()
def delete_car(car_id):
    try:
        car = Car.query.get_or_404(car_id)

        detail = {
            'id': car.id,
            'make_id': car.make_id,
            'model_id': car.model_id,
            'make': car.make.name,
            'model': car.model.name,
            'year': car.year,
            'category': car.category
        }

        db.session.delete(car)
        db.session.commit()

        return jsonify({
            'message': 'Car deleted successfully',
            'deleted': CarSchema().dump(detail)
        }), 200
        
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'message': 'Database error occurred'}), 500
