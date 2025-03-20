import os
import sys
import unittest
from app import create_app, db

class AppFunctionalityTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_app_exists(self):
        self.assertIsNotNone(self.app)
    
    def test_app_is_testing(self):
        self.assertTrue(self.app.config['TESTING'])
    
    def test_db_connection(self):
        # This test will fail if the database connection is not working
        result = db.engine.execute('SELECT 1').fetchone()
        self.assertEqual(result[0], 1)
    
    def test_blueprints_registered(self):
        # Test that all expected blueprints are registered
        expected_blueprints = ['main', 'auth', 'dashboard', 'employees', 'evaluations', 'reports']
        for blueprint in expected_blueprints:
            self.assertIn(blueprint, self.app.blueprints)

if __name__ == '__main__':
    unittest.main()