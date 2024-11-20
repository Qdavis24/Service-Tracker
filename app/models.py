from sqlalchemy import LargeBinary, TIMESTAMP
from flask_login import UserMixin
# extensions
from .extensions import db


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, unique=False, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)
    vehicles = db.relationship("Vehicles", backref="owner", lazy=True, cascade="all, delete-orphan")
    services = db.relationship("Services", backref="owner", lazy=True, cascade="all, delete-orphan")


class Vehicles(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    owner_id = db.Column(db.ForeignKey('users.id'), nullable=False, unique=False)
    year = db.Column(db.String, unique=False, nullable=False)
    make = db.Column(db.String, unique=False, nullable=False)
    model = db.Column(db.String, unique=False, nullable=False)
    picture_id = db.Column(db.ForeignKey('pictures.id'), nullable=True, unique=True)
    picture = db.relationship("Pictures", foreign_keys=[picture_id], cascade="all, delete-orphan", single_parent=True)
    mileage = db.Column(db.Integer, unique=False, nullable=True)
    services = db.relationship("Services", backref="vehicle", lazy=True, cascade="all, delete-orphan")


class Services(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.ForeignKey('users.id'), nullable=False, unique=False)
    vehicle_id = db.Column(db.ForeignKey("vehicles.id"), nullable=False, unique=False)
    date = db.Column(TIMESTAMP, nullable=False, unique=False)
    mileage = db.Column(db.Integer, nullable=True, unique=False)
    service = db.Column(db.String, nullable=False, unique=False)
    story = db.Column(db.String, nullable=False, unique=False)
    picture_id = db.Column(db.ForeignKey('pictures.id'), nullable=True, unique=True)
    picture = db.relationship("Pictures", foreign_keys=[picture_id], cascade="all, delete-orphan", single_parent=True)


class Pictures(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    picture = db.Column(LargeBinary, nullable=True, unique=False)
