from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    ForeignKey
)
from sqlalchemy.orm import relationship
from app.models import Base


class Make(Base):

    __tablename__ = 'makes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False, index=True)

    models = relationship("CarModel", back_populates="make")
    cars = relationship("Car", back_populates="make")


class CarModel(Base):

    __tablename__ = 'models'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)
    make_id = Column(Integer, ForeignKey('makes.id'), nullable=False, index=True)

    make = relationship('Make', back_populates='models')
    cars = relationship('Car', back_populates='model')


class Car(Base):

    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True, index=True)
    make_id = Column(Integer, ForeignKey('makes.id'), nullable=False)
    model_id = Column(Integer, ForeignKey('models.id'), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    category = Column(String(64), nullable=False)
    
    make = relationship("Make", back_populates="cars")
    model = relationship("CarModel", back_populates="cars")
