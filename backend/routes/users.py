from flask import Blueprint

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    return {'message': 'Perfil no implementado aún'}, 501