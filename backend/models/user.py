from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from backend.extensions import db


class User(db.Model):
    """Modelo de Usuario."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    profile_bio = db.Column(db.Text, default="")
    profile_html = db.Column(db.Text, default="")
    avatar_url = db.Column(db.String(255), default="")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    songs = db.relationship(
        "Song",
        backref="creator",
        lazy=True,
        foreign_keys="Song.user_id"
    )

    comments = db.relationship(
        "Comment",
        backref="author",
        lazy=True
    )

    def set_password(self, password):
        """Hashear contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verificar contraseña."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convertir usuario a diccionario."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "profile_bio": self.profile_bio,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat()
            if self.created_at else None
        }