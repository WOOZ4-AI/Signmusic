from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear app Flask
app = Flask(__name__)

# Configuración
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///signmusic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'tu-secreto-super-seguro-cambiar-en-produccion')

# Inicializar extensiones
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Importar modelos
from models.user import User
from models.song import Song
from models.comment import Comment

# Importar rutas
from routes.auth import auth_bp
from routes.songs import songs_bp
from routes.users import users_bp

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(songs_bp, url_prefix='/api/songs')
app.register_blueprint(users_bp, url_prefix='/api/users')

# Ruta de prueba
@app.route('/api/health', methods=['GET'])
def health():
    return {'status': 'ok', 'message': '🎵 SIGNMUSIC Backend funcionando!'}, 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)