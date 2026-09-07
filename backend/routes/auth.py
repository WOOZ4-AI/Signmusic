from datetime import timedelta

from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

from extensions import db
from models.user import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Registrar nuevo usuario."""
    data = request.get_json()

    if (
        not data
        or not data.get("username")
        or not data.get("email")
        or not data.get("password")
    ):
        return {"error": "Faltan campos requeridos"}, 400

    if User.query.filter_by(username=data["username"]).first():
        return {"error": "El usuario ya existe"}, 409

    if User.query.filter_by(email=data["email"]).first():
        return {"error": "El email ya está registrado"}, 409

    user = User(
        username=data["username"],
        email=data["email"],
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return {
        "message": "Usuario registrado exitosamente",
        "user": user.to_dict(),
    }, 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login de usuario."""
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return {"error": "Email y password requeridos"}, 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return {"error": "Email o contraseña incorrectos"}, 401

    access_token = create_access_token(
    identity=str(user.id),
    expires_delta=timedelta(days=30)
)

    return {
        "message": "Login exitoso",
        "access_token": access_token,
        "user": user.to_dict(),
    }, 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obtener usuario actual"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return {'error': 'Usuario no encontrado'}, 404

    return {'user': user.to_dict()}, 200