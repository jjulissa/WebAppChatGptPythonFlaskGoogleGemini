# app/__init__.py 

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from datetime import timedelta 
from .routes.main import main_bp 
import os

from .models import db 

def create_app():
    app = Flask(__name__)

    # Configuración principal (usa variables de entorno para producción)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-super-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///chat.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)

    # Inicialización de extensiones
    db.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)

    # Registro de Blueprints
    from .routes.auth import auth_bp
    from .routes.chat import chat_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp) 
    app.register_blueprint(main_bp)

    return app

