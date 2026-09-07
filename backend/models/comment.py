from datetime import datetime

from backend.extensions import db


class Comment(db.Model):
    """Modelo de Comentario."""

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    song_id = db.Column(
        db.Integer,
        db.ForeignKey("songs.id"),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def to_dict(self):
        """Convertir comentario a diccionario."""
        return {
            "id": self.id,
            "content": self.content,
            "author": self.author.username if self.author else None,
            "created_at": self.created_at.isoformat()
            if self.created_at else None
        }