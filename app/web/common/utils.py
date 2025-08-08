from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from app.models.db import db

def paginate(query):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('limit', 20))
    return query.paginate(page=page, per_page=per_page, error_out=False)


def validate_make_model(make_id, model_id):
    from app.models.cars import Make, CarModel
    make = Make.query.get(make_id)
    model = CarModel.query.get(model_id)
    return make and model and model.make_id == make.id
