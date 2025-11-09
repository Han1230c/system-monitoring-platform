"""
Server configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    # For local testing, use SQLite
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        # Use SQLite for local development
        basedir = os.path.abspath(os.path.dirname(__file__))
        DATABASE_URL = f'sqlite:///{os.path.join(basedir, "monitoring.db")}'
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Server configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('FLASK_ENV', 'production') == 'development'
