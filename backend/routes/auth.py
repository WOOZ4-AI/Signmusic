from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    return {'message': 'Registro no implementado aún'}, 501

@auth_bp.route('/login', methods=['POST'])
def login():
    return {'message': 'Login no implementado aún'}, 501