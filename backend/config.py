import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///signmusic.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')

class DevelopmentConfig(Config):
    """Configuración desarrollo"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuración producción"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Configuración testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'