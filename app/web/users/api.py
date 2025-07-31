from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.models.users import User
from app.models.db import db
from flask_jwt_extended import jwt_required
from app.web.common.jwt import generate_token
from app.web.users.schemas import (
    UserRegisterSchema,
    UserLoginSchema,
    UserSchema
)
from bcrypt import hashpw, gensalt, checkpw

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        validated = UserRegisterSchema().load(data)
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400

    if User.query.filter_by(username=validated['username']).first():
        return jsonify({'message': 'User already exists'}), 409

    if len(validated['password']) < 6:
        return jsonify({'message': 'Password must be at least 6 characters long'}), 400

    hashed = hashpw(validated['password'].encode('utf-8'), gensalt())
    user = User(
        username=validated['username'],
        password_hash=hashed.decode('utf-8')
    )

    db.session.add(user)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'message': 'Database error occurred'}), 500

    return jsonify({
        'message': 'User created successfully',
        'user': UserSchema().dump(user)
    }), 201


@users_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        validated = UserLoginSchema().load(data)
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400

    user = User.query.filter_by(username=validated['username']).first()
    if not user or not checkpw(validated['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = generate_token(identity=user.id)
    return jsonify({
        'message': 'Login successful',
        'access_token': token,
        'user': UserSchema().dump(user)
    }), 200
