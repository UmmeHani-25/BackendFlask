from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from app.models.cars import Make, CarModel
from app.models.db import db


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

    @validates("make")
    def validate_make(self, value, **kwargs):
        make = db.session.query(Make).filter_by(name=value).first()
        if not make:
            raise ValidationError(f"Make '{value}' not found")

    @validates_schema
    def validate_make_model(self, data, **kwargs):
        make = db.session.query(Make).filter_by(name=data.get("make")).first()
        if not make:
            return  # Already handled in validate_make
        model = db.session.query(CarModel).filter_by(
            name=data.get("model"),
            make_id=make.id
        ).first()
        if not model:
            raise ValidationError(
                f"Model '{data.get('model')}' not found for make '{data.get('make')}'.",
                field_name="model"
            )


class CarUpdateSchema(Schema):
    make_id = fields.Int()
    model_id = fields.Int()
    year = fields.Int(validate=validate.Range(min=1900, max=2100))
    category = fields.Str(allow_none=True)

    @validates_schema
    def validate_make_model(self, data, **kwargs):
        model_id = data.get("model_id")
        make_id = data.get("make_id")

        if model_id:
            model = db.session.get(CarModel, model_id)
            if not model:
                raise ValidationError(f"Model with ID '{model_id}' not found", field_name="model_id")
            if make_id and model.make_id != make_id:
                raise ValidationError("Model does not belong to the given make.", field_name="model_id")

