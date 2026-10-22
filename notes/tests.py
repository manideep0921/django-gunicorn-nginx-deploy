import json

from django.test import TestCase

from .models import Note


class HealthTests(TestCase):
    def test_healthz(self):
        r = self.client.get('/healthz')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['status'], 'ok')

    def test_readyz_checks_database(self):
        r = self.client.get('/readyz')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['status'], 'ready')


class NotesApiTests(TestCase):
    def test_create_and_list(self):
        r = self.client.post('/api/notes', data=json.dumps({'title': 'hello'}),
                             content_type='application/json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Note.objects.count(), 1)
        listing = self.client.get('/api/notes').json()['results']
        self.assertEqual(listing[0]['title'], 'hello')

    def test_title_required(self):
        r = self.client.post('/api/notes', data=json.dumps({'title': '  '}),
                             content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_invalid_json(self):
        r = self.client.post('/api/notes', data='{bad', content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_method_not_allowed(self):
        self.assertEqual(self.client.delete('/api/notes').status_code, 405)
