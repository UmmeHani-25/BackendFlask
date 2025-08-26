from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    DateTime
)
from werkzeug.security import (
    generate_password_hash, 
    check_password_hash 
)
from datetime import datetime
from app.models import Base


class User(Base):
    
    ID_KEY = 'id'
    USERNAME_KEY = 'username'
    CREATED_AT_KEY = 'created_at'

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_json(self):
        return {
            self.ID_KEY: self.id,
            self.USERNAME_KEY: self.username,
            self.CREATED_AT_KEY: str(self.created_at)
        }
