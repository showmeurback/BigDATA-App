from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')  # user, admin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('datasets', lazy=True))

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # e.g., 'В работе', 'Завершена', 'Ошибка'

class ProjectType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # e.g., 'Анализ данных', 'ML проект', 'Визуализация'

class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # e.g., 'regression', 'classification'
    target_column = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=False)
    dataset = db.relationship('Dataset', backref=db.backref('models', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('models', lazy=True))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    status = db.relationship('Status', backref=db.backref('models', lazy=True))
    project_type_id = db.Column(db.Integer, db.ForeignKey('project_type.id'), nullable=False)
    project_type = db.relationship('ProjectType', backref=db.backref('models', lazy=True))