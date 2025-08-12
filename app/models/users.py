from datetime import datetime
from app.models.db import db


class User(db.Model):
    
    ID_KEY = 'id'
    USERNAME_KEY = 'username'
    CREATED_AT_KEY = 'created_at'

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        return {
            self.ID_KEY: self.id,
            self.USERNAME_KEY: self.username,
            self.CREATED_AT_KEY: str(self.created_at)
        }
