from marshmallow import Schema, fields

class UserRegisterSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    created_at = fields.DateTime()
