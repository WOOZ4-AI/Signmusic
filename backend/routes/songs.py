from flask import Blueprint

songs_bp = Blueprint('songs', __name__)

@songs_bp.route('/search', methods=['GET'])
def search():
    return {'message': 'Búsqueda no implementada aún'}, 501

@songs_bp.route('/process', methods=['POST'])
def process():
    return {'message': 'Procesamiento no implementado aún'}, 501