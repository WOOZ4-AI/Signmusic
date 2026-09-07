from datetime import datetime

from backend.extensions import db


class Song(db.Model):
    """Modelo de Canción."""

    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)

    url_source = db.Column(db.String(500), nullable=False)
    source_type = db.Column(db.String(50), nullable=False)

    duration = db.Column(db.Integer, default=0)

    audio_path = db.Column(db.String(500), default="")
    video_path = db.Column(db.String(500), default="")
    animation_json = db.Column(db.Text, default="")

    language = db.Column(db.String(10), default="en")
    sign_language = db.Column(db.String(10), default="dgs")

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    comments = db.relationship(
        "Comment",
        backref="song",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Convertir canción a diccionario."""
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "duration": self.duration,
            "creator": self.creator.username if self.creator else None,
            "views": self.views,
            "likes": self.likes,
            "created_at": self.created_at.isoformat()
            if self.created_at else None
        }