from marshmallow import Schema, fields, validate

class CarSchema(Schema):
    id = fields.Int(dump_only=True)
    make = fields.Str()
    model = fields.Str()
    category = fields.Str(allow_none=True)
    year = fields.Int()

class CarCreateSchema(Schema):
    make_id = fields.Int(required=True, validate=validate.Range(min=1))
    model_id = fields.Int(required=True, validate=validate.Range(min=1))
    year = fields.Int(required=True, validate=validate.Range(min=1900, max=2030))
    category = fields.Str(missing=None, allow_none=True)

class CarUpdateSchema(Schema):
    make_id = fields.Int(validate=validate.Range(min=1))
    model_id = fields.Int(validate=validate.Range(min=1))
    year = fields.Int(validate=validate.Range(min=1900, max=2030))
    category = fields.Str(allow_none=True)