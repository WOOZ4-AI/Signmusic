from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Song(db.Model):
    """Modelo de Canción"""
    __tablename__ = 'songs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    url_source = db.Column(db.String(500), nullable=False)  # URL de YouTube/Spotify
    source_type = db.Column(db.String(50), nullable=False)  # youtube, spotify
    duration = db.Column(db.Integer, default=0)  # segundos
    
    # Archivos generados
    audio_path = db.Column(db.String(500), default='')
    video_path = db.Column(db.String(500), default='')  # Video con avatar
    animation_json = db.Column(db.Text, default='')  # JSON de keyframes
    
    # Metadatos
    language = db.Column(db.String(10), default='en')
    sign_language = db.Column(db.String(10), default='dgs')  # DGS, ASL, etc.
    
    # Usuario que subió
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Stats
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    comments = db.relationship('Comment', backref='song', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'duration': self.duration,
            'creator': self.creator.username,
            'views': self.views,
            'likes': self.likes,
            'created_at': self.created_at.isoformat()
        }