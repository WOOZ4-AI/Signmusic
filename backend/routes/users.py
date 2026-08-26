from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import db
from models.user import User

users_bp = Blueprint('users', __name__)

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obtener perfil de usuario"""
    user = User.query.get(user_id)
    
    if not user:
        return {'error': 'Usuario no encontrado'}, 404
    
    return {'user': user.to_dict()}, 200

@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Actualizar perfil del usuario actual"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return {'error': 'Usuario no encontrado'}, 404
    
    data = request.get_json()
    
    if 'profile_bio' in data:
        user.profile_bio = data['profile_bio']
    
    if 'profile_html' in data:
        user.profile_html = data['profile_html']
    
    if 'avatar_url' in data:
        user.avatar_url = data['avatar_url']
    
    db.session.commit()
    
    return {
        'message': 'Perfil actualizado',
        'user': user.to_dict()
    }, 200