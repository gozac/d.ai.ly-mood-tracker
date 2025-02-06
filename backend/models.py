from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import sqlite3
import json
from datetime import datetime

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
    def create(username, password):
        conn = sqlite3.connect('instance/database.sqlite')
        c = conn.cursor()
        try:
            c.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

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