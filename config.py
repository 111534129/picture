import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-prod'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database Configuration
    # Format: mysql+mysqlconnector://user:password@host/db_name
    # Defaulting to a local mysql setup, user needs to update .env or this string
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:@localhost/photo_platform'
    
    # Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload setup
