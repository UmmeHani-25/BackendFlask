import logging
from flask_smorest import Blueprint
from sqlalchemy.exc import SQLAlchemyError
from app.models.users import User
from app.models.db import db
from app.web.common.jwt import generate_token
from bcrypt import hashpw, gensalt, checkpw
from app.web.users.schemas import (
    UserRegisterSchema,
    UserLoginSchema,
    UserLoginResponseSchema
)

logger = logging.getLogger(__name__)

users_bp = Blueprint('users', __name__)


@users_bp.route('/register', methods=['POST'])
@users_bp.arguments(UserRegisterSchema)
def register(validated):
        
        if db.session.query(User).filter_by(username=validated['username']).first():
            logger.warning(f"Username {validated['username']} already exists")
            return {'message': 'Username already exists'}, 400

        if len(validated['password']) < 6:
            logger.warning("Password must be at least 6 characters long")
            return {'message': 'Password must be at least 6 characters long'}, 400

        hashed = hashpw(validated['password'].encode('utf-8'), gensalt())

        user_data = {
            'username': validated['username'],
            'password_hash': hashed.decode('utf-8')
        }

        user = User(**user_data)
        db.session.add(user)
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            logger.error("Database error occurred while registering user")

        return user.to_json(), 201


@users_bp.route('/login', methods=['POST'])
@users_bp.arguments(UserLoginSchema)
@users_bp.response(200, UserLoginResponseSchema)
def login(validated):
    user = db.session.query(User).filter_by(username=validated['username']).first()
    if not user or not checkpw(validated['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        logger.warning("Invalid username or password")
        return {'message': 'Invalid username or password'}, 401

    user.token = generate_token(identity=user.id)

    return user
