from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework.test import APIClient


class HealthEndpointTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_is_available_without_login(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_health_rejects_post(self):
        response = self.client.post(reverse("health"), {}, format="json")

        self.assertEqual(response.status_code, 405)
