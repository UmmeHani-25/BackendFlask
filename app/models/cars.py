from app.models.db import db

class Make(db.Model):
    __tablename__ = 'makes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

class Model(db.Model):
    __tablename__ = 'models'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    make_id = db.Column(db.Integer, db.ForeignKey('makes.id'), nullable=False)
    make = db.relationship('Make', backref=db.backref('models', lazy=True))

class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.Integer, primary_key=True)
    make_id = db.Column(db.Integer, db.ForeignKey('makes.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(255), nullable=True)
    
    make = db.relationship('Make', foreign_keys=[make_id])
    model = db.relationship('Model', foreign_keys=[model_id])
