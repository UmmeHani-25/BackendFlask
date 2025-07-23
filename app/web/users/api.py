from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
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

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def register():
    try:
        data = UserRegisterSchema().load(request.json or {})
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400

    try:
        existing = User.query.filter_by(username=data['username']).first()
        if existing:
            return jsonify({'message': 'User already exists'}), 409

        # Validate password strength
        if len(data['password']) < 6:
            return jsonify({'message': 'Password must be at least 6 characters long'}), 400

        user = User(
            username=data['username'],
            password_hash=generate_password_hash(data['password'])
        )
        db.session.add(user)
        db.session.commit()

        # Return user without password
        result = UserSchema().dump(user)
        return jsonify({
            'message': 'User created successfully',
            'user': result
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': 'Database error occurred'}), 500


@users_bp.route('/login', methods=['POST'])
def login():
    try:
        data = UserLoginSchema().load(request.json or {})
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400

    try:
        user = User.query.filter_by(username=data['username']).first()
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'message': 'Invalid credentials'}), 401

        token = generate_token(identity=str(user.id))
        return jsonify({
            'message': 'Login successful',
            'access_token': token,
            'user': UserSchema().dump(user)
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Login failed'}), 500