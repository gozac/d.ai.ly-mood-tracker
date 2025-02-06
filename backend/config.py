import os
from dotenv import load_dotenv
from datetime import timedelta
from database import init_db

load_dotenv()
init_db()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'votre-clé-secrète')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.sqlite'
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # Durée de validité du token