import unittest
from app import create_app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_root_url(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>', response.data)

    def test_status_api(self):
        response = self.client.get('/api/v1/status')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('status', json_data)
        self.assertIn('timestamp', json_data)