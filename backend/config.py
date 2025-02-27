import os
from dotenv import load_dotenv
from datetime import timedelta
from database import init_db

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'votre-clé-secrète')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'max_overflow': 2,
        'pool_timeout': 30,
        'pool_recycle': 1800,
    }
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    FRONTEND_URL = os.getenv('FRONTEND_URL')
    JWT_SECRET_KEY = os.getenv('JWT_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # Durée de validité du token