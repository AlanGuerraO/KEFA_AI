"""Casos Django para nuevos resultados de Gemini; requieren dependencias backend."""

from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from ai_api.views import tool_calling
from config.gemini_client import GeminiAPIError
from orchestrator.decision_flow import DecisionType, OrchestratorDecision


class TestGeminiAPIView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = Mock(pk=1, is_authenticated=True, is_active=True)
        self.user.get_all_permissions.return_value = set()

    def post(self, data):
        request = self.factory.post('/api/ai/tool-calling/', data, format='json')
        force_authenticate(request, user=self.user)
        return tool_calling(request)

    @patch('ai_api.views.ToolCallingBridge')
    def test_text_from_gemini_is_delivered_to_frontend(self, bridge):
        bridge.return_value.procesar.return_value = [{
            'decision': OrchestratorDecision(DecisionType.RESPOND, reason='¿A qué hora termina?'),
            'status': 'response', 'message': '¿A qué hora termina?'
        }]
        response = self.post({'mensaje': 'Agenda reunión'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['resultados'][0]['decision'], 'respond')
        self.assertEqual(response.data['resultados'][0]['message'], '¿A qué hora termina?')

    @patch('ai_api.views.is_dispatch_enabled', return_value=True)
    @patch('ai_api.views.ToolCallingBridge')
    def test_text_response_does_not_trigger_n8n_even_in_execute_mode(self, bridge, enabled):
        bridge.return_value.procesar.return_value = [{
            'decision': OrchestratorDecision(DecisionType.RESPOND, reason='Falta título'),
            'status': 'response', 'message': 'Falta título'
        }]
        response = self.post({'mensaje': 'Crea una tarea', 'ejecutar': True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['resultados'][0]['decision'], 'respond')

    @patch('ai_api.views.ToolCallingBridge')
    def test_gemini_quota_is_reported_as_http_429(self, bridge):
        bridge.return_value.procesar.side_effect = GeminiAPIError('Cuota de Gemini agotada.', 429)
        response = self.post({'mensaje': 'Hola'})
        self.assertEqual(response.status_code, 429)
        self.assertIn('Cuota', response.data['error'])

    @patch('ai_api.views.ToolCallingBridge')
    def test_gemini_invalid_key_reported_as_502(self, bridge):
        bridge.return_value.procesar.side_effect = GeminiAPIError('La clave de Gemini no es válida.', 401)
        response = self.post({'mensaje': 'Hola'})
        self.assertEqual(response.status_code, 502)
        self.assertNotIn('sk-', response.data['error'])
