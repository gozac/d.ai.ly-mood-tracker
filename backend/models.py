from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base, scoped_session, sessionmaker
from datetime import datetime
from passlib.context import CryptContext
from config import Config

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

Base = declarative_base()

# Configuration de SQLAlchemy avec l'URL de la base de données depuis Config
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    # Configuration du pool de connexions pour SQLite
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=1800
    # Suppression de connect_args qui n'est pas compatible avec SQLite
)

db_session = scoped_session(sessionmaker(bind=engine))
Base.query = db_session.query_property()  # Ajoute la propriété query à tous les modèles

def init_db():
    # Import ici pour éviter les imports circulaires
    import models
    Base.metadata.create_all(bind=engine)

class User(Base, UserMixin):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(128))
    reports = relationship('Report', backref='author', lazy=True)
    evaluations = relationship('Evaluation', backref='user', lazy=True)

    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

    @staticmethod
    def get(user_id):
        return db_session.query(User).get(user_id)

    @staticmethod
    def get_by_username(username):
        return db_session.query(User).filter_by(username=username).first()

    @staticmethod
    def create(username: str, password: str) -> bool:
        try:
            existing_user = User.get_by_username(username)
            if existing_user:
                return False
                
            user = User(username, pwd_context.hash(password))
            db_session.add(user)
            db_session.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            db_session.rollback()
            return False

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            print(f"Password verification error: {e}")
            return False

class Report(Base):
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    answers = Column(Text)
    summary = Column(Text, nullable=False)

class Evaluation(Base):
    __tablename__ = 'evaluations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    content = Column(Text, nullable=False)

class Goal(Base):
    __tablename__ = 'goals'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    status = Column(String(20), default='active')  # 'active' ou 'completed'
    
    # Relation avec l'utilisateur
    user = relationship('User', backref='goals')