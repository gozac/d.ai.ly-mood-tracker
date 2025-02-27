import unittest
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base, scoped_session, sessionmaker

import os
import sys
# Ajouter le répertoire parent (racine du projet) au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import User, Base


engine = create_engine(
    'sqlite:///test.db',
    # Configuration du pool de connexions pour SQLite
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=1800
    # Suppression de connect_args qui n'est pas compatible avec SQLite
)
# Configurez une base de données de test
db_session = scoped_session(sessionmaker(bind=engine))

class TestModels(unittest.TestCase):
    def setUp(self):
        """Configuration initiale avant chaque test"""
        f = open("test.db", "w")   # 'r' for reading and 'w' for writing
        f.close()
        
        Base.query = db_session.query_property() 
        Base.metadata.create_all(bind=engine)

    def tearDown(self):
        """Nettoyage après chaque test"""
        db_session.remove()
        Base.metadata.drop_all(bind=engine)
        os.remove("test.db")


    def test_create_user(self):
        """Test la création d'un utilisateur"""
        # 1. Création d'un utilisateur
        user = User(username="test_user", password_hash="123")
        
        # 2. Sauvegarde dans la base de données
        db_session.add(user)
        db_session.commit()

        # 3. Récupération de l'utilisateur depuis la base
        saved_user = User.query.filter_by(username="test_user").first()
        
        # 4. Vérifications
        self.assertIsNotNone(saved_user)  # Vérifie que l'utilisateur existe
        self.assertEqual(saved_user.password_hash, "123")  # Vérifie les données 