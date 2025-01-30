import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'votre-clé-secrète')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.sqlite'
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')