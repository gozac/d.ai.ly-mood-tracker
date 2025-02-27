import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_service import generate_summary, generate_evaluation

class TestAIService(unittest.TestCase):
    @patch('ai_service.client.chat.completions.create')
    def test_generate_summary(self, mock_create):
        """Test la génération de résumé"""
        # Configuration du mock
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Résumé test"
        mock_create.return_value = mock_response

        # Données de test
        test_answers = {
            "mood": 7,
            "q1": "J'ai terminé un projet important",
            "q2": "La journée était productive",
            "q3": "Je me sens satisfait"
        }
        test_objectifs = ["Apprendre Python", "Faire du sport"]

        # Test de la fonction
        result = generate_summary(test_answers, test_objectifs)

        # Vérifications
        self.assertEqual(result, "Résumé test")
        mock_create.assert_called_once()
        
        # Vérification des arguments passés à l'API
        call_args = mock_create.call_args[1]
        self.assertEqual(call_args['model'], "gpt-4")
        self.assertEqual(len(call_args['messages']), 2)
        self.assertIn("system", call_args['messages'][0]['role'])
        self.assertIn("user", call_args['messages'][1]['role'])
        self.assertIn(test_answers["q1"], call_args['messages'][1]['content'])

    @patch('ai_service.client.chat.completions.create')
    def test_generate_evaluation(self, mock_create):
        """Test la génération d'évaluation avec différents conseillers"""
        # Configuration du mock
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Évaluation test"
        mock_create.return_value = mock_response

        # Données de test
        test_history = [
            "Jour 1: Journée productive",
            "Jour 2: Journée difficile",
            "Jour 3: Journée moyenne"
        ]

        # Test avec différents conseillers
        for advisor_id in range(3):  # Test avec les 3 premiers conseillers
            with self.subTest(advisor_id=advisor_id):
                result = generate_evaluation(test_history, advisor_id)
                
                # Vérifications
                self.assertEqual(result, "Évaluation test")
                self.assertTrue(mock_create.called)
                
                # Vérification des arguments passés à l'API
                call_args = mock_create.call_args[1]
                self.assertEqual(call_args['model'], "gpt-4")
                self.assertEqual(len(call_args['messages']), 2)
                self.assertIn("system", call_args['messages'][0]['role'])
                self.assertIn("user", call_args['messages'][1]['role'])
                
                # Vérifier que l'historique est bien inclus
                for day in test_history:
                    self.assertIn(day, call_args['messages'][1]['content'])
                
            mock_create.reset_mock()

    @patch('ai_service.client.chat.completions.create')
    def test_error_handling(self, mock_create):
        """Test la gestion des erreurs"""
        # Simuler une erreur d'API
        mock_create.side_effect = Exception("API Error")

        # Test avec des données minimales
        test_answers = {
            "mood": 5,
            "q1": "Test",
            "q2": "Test",
            "q3": "Test"
        }
        test_objectifs = ["Test"]

        # Vérifier que l'erreur est gérée correctement
        with self.assertRaises(Exception):
            generate_summary(test_answers, test_objectifs)

if __name__ == '__main__':
    unittest.main() 