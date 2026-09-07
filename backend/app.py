from flask import Flask
from dotenv import load_dotenv
import os

from backend.extensions import db, jwt

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///signmusic.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY",
    "tu-secreto-super-seguro-cambiar-en-produccion"
)

db.init_app(app)
jwt.init_app(app)

# Importar modelos para que SQLAlchemy conozca todas las tablas
from backend.models.user import User
from backend.models.song import Song
from backend.models.comment import Comment

# Importar rutas
from backend.routes.auth import auth_bp
from backend.routes.songs import songs_bp
from backend.routes.users import users_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(songs_bp, url_prefix="/api/songs")
app.register_blueprint(users_bp, url_prefix="/api/users")


@app.route("/api/health", methods=["GET"])
def health():
    return {
        "status": "ok",
        "message": "🎵 SIGNMUSIC Backend funcionando!"
    }, 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5000)