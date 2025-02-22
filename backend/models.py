from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import sqlite3
import json
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @property
    def is_active(self):
        return True
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

    @staticmethod
    def get(user_id):
        conn = sqlite3.connect('instance/database.sqlite')
        c = conn.cursor()
        user = c.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user:
            return User(user[0], user[1], user[2])
        return None

    @staticmethod
    def get_by_username(username):
        conn = sqlite3.connect('instance/database.sqlite')
        c = conn.cursor()
        user = c.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user:
            return User(user[0], user[1], user[2])
        return None

    @staticmethod
    def create(username: str, password: str) -> bool:
        conn = sqlite3.connect('instance/database.sqlite')
        c = conn.cursor()
        
        # Vérifier si l'utilisateur existe déjà
        if c.execute('SELECT 1 FROM users WHERE username = ?', (username,)).fetchone():
            conn.close()
            return False
        
        try:
            # Hasher le mot de passe
            hashed_password = pwd_context.hash(password)
            
            c.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, hashed_password)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            print(f"Password verification error: {e}")
            return False

class Report:
    def __init__(self, user_id, date, answers, summary):
        self.user_id = user_id
        self.date = date
        self.answers = answers
        self.summary = summary

class Evaluation:
    def __init__(self, user_id, date, content):
        self.user_id = user_id
        self.date = date
        self.content = content