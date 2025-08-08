from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from app.models.db import db
from app.models.cars import Make, CarModel


class CarSchema(Schema):

    id = fields.Int(dump_only=True)
    make_id = fields.Int(required=True)
    model_id = fields.Int(required=True)
    year = fields.Int(required=True, validate=validate.Range(min=1900, max=2100))
    category = fields.Str(allow_none=True)


class CarCreateSchema(Schema):

    make = fields.Str(required=True)
    model = fields.Str(required=True)
    year = fields.Int(validate=validate.Range(min=1900, max=2100))
    category = fields.Str(required=True)


class CarUpdateSchema(Schema):
    
    make_id = fields.Int()
    model_id = fields.Int()
    year = fields.Int(validate=validate.Range(min=1900, max=2100))
    category = fields.Str(allow_none=True)
