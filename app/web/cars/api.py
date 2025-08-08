from os import abort
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from app.models.db import db
from app.models.cars import Make, CarModel, Car
from app.web.cars.schemas import CarSchema, CarCreateSchema, CarUpdateSchema
from app.web.common.utils import paginate, validate_make_model
import logging

logger = logging.getLogger(__name__)

cars_bp = Blueprint('cars', __name__)


@cars_bp.route('/', methods=['GET'])
@cars_bp.response(200, CarSchema(many=True))
@jwt_required()
def get_cars():

    logger.info("Fetching all cars")
    return paginate(db.session.query(Car)).items


@cars_bp.route('/<int:car_id>', methods=['GET'])
@cars_bp.response(200, CarSchema())
@jwt_required()
def get_car(car_id):

    logger.info(f"Fetching car with ID: {car_id}")

    car = db.session.get(Car, car_id)
    if not car:
        logger.warning(f"Car with ID {car_id} not found")
    return car


@cars_bp.route('/', methods=['POST'])
@jwt_required()
@cars_bp.arguments(CarCreateSchema) 
@cars_bp.response(201, CarSchema())
def create_car(data):
    
    logger.info("Creating a new car with data: %s", data)
    
    make = db.session.query(Make).filter_by(name=data['make']).first()
    if not make:
        logger.warning(f"Make '{data['make']}' does not exist")
        return {"message": f"Make '{data['make']}' not found"}, 400
    
    model = db.session.query(CarModel).filter_by(name=data['model'], make_id=make.id).first()
    if not model:
        logger.warning(f"Model '{data['model']}' does not exist for Make '{data['make']}'")
        return {"message": f"Model '{data['model']}' not found for Make '{data['make']}'"}, 400
    
    car = Car(
        make_id=make.id,
        model_id=model.id,
        year=data['year'],
        category=data.get('category')
    )
    
    db.session.add(car)
    db.session.commit()
    
    return car

@cars_bp.route('/<int:car_id>', methods=['PUT'])
@jwt_required()
@cars_bp.arguments(CarUpdateSchema(partial=True))
@cars_bp.response(200, CarCreateSchema())
def update_car(data, car_id):

    logger.info(f"Updating car with ID: {car_id} with data: {data}")

    car = db.session.get(Car, car_id)
    if not car:
        logger.warning(f"Car with ID {car_id} not found")

    if 'make_id' in data or 'model_id' in data:
        make_id = data.get('make_id', car.make_id)
        model_id = data.get('model_id', car.model_id)
        if not validate_make_model(make_id, model_id):
            logger.warning("Invalid make_id or model_id combination")

    for key, val in data.items():
        setattr(car, key, val)

    db.session.commit()
    return car


@cars_bp.route("/<int:car_id>", methods=["DELETE"])
@jwt_required()
@cars_bp.response(200, CarCreateSchema())
def delete_car(car_id):
    logger.info(f"Deleting car with ID: {car_id}")
    car = Car.query.get(car_id)
    
    if not car:
        logger.warning(f"Car with ID {car_id} not found")
        return {"error": f"Car with ID {car_id} not found"}, 404
    
    db.session.delete(car)
    db.session.commit()
    logger.info(f"Car with ID {car_id} deleted successfully")
    
    return {"message": f"Car with ID {car_id} deleted successfully"}, 200

