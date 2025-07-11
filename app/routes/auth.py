# app/routes/auth.py 

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
) 
from app.models import db, User 

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email y contraseña requeridos"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Usuario ya existe"}), 409

    hashed_password = generate_password_hash(password)
    user = User(email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "Usuario registrado"}), 201 



@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Credenciales inválidas"}), 401

    # El identity será el id del usuario
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=user_id)
    return jsonify(access_token=new_access_token), 200 
