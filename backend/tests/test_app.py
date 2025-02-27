import unittest
from fastapi.testclient import TestClient
import os
import sys
import json

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        """Configuration initiale avant chaque test"""
        self.client = TestClient(app)

    def test_home_route(self):
        """Test la route principale"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 404)

    def test_message_route(self):
        """Test la route message"""
        response = self.client.post(
            '/message',
            params={'message': 'Hello World'}  # Changé de json à params car l'API attend un str
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Hello World')

    def test_verify_token_unauthorized(self):
        """Test la route verify-token sans authentification"""
        response = self.client.get('/verify-token')
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_register(self):
        """Test la route register"""
        # D'abord, supprimons l'utilisateur s'il existe déjà
        from models import User, db_session
        db_session.query(User).filter_by(username='testuser').delete()
        db_session.commit()

        response = self.client.post(
            '/register',
            json={
                "username": "testuser",
                "password": "testpassword"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'User created successfully')

    def tearDown(self):
        """Nettoyage après les tests"""
        from models import User, db_session
        db_session.query(User).filter_by(username='testuser').delete()
        db_session.commit()

if __name__ == '__main__':
    unittest.main()
        