# Tablas de mi base de datos

from flask_security import SQLAlchemyUserDatastore, RoleMixin, UserMixin
from app import db

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id')))

# Tabla de usuarios
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    plan = db.Column(db.String(100), nullable=False)
    numero = db.Column(db.String(100), nullable=False)
    hash = db.Column(db.String(999), nullable=False)
    active = db.Column(db.Boolean)
    fecha = db.Column(db.DateTime, nullable=False)

    stats = db.relationship('Stats', backref='user')
    roles = db.relationship('Roles', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    turnos = db.relationship('Schedule', backref='user')

# Tabla de horarios
class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dia = db.Column(db.Date, nullable=False)
    hora = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)

    def __init__(self, user_id, dia, hora, tipo):
        self.user_id = user_id
        self.dia = dia
        self.hora = hora
        self.tipo = tipo


# Tabla de estadísticas
class Stats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    peso = db.Column(db.Float, nullable=False)
    porcentaje_grasa = db.Column(db.Float, nullable=False)
    masa_muscular = db.Column(db.Float, nullable=False)
    masa_osea = db.Column(db.Float, nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    grasa_visceral = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, user_id, peso, porcentaje_grasa, masa_muscular, masa_osea, edad, grasa_visceral, time):
        self.user_id = user_id
        self.peso = peso
        self.porcentaje_grasa = porcentaje_grasa
        self.masa_muscular = masa_muscular
        self.masa_osea = masa_osea
        self.edad = edad
        self.grasa_visceral = grasa_visceral
        self.time = time

# Tabla de roles y permisos
class Roles(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))

class Frases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    frase = db.Column(db.String(500))

user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)