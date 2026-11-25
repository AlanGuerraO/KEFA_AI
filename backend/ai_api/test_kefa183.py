"""KEFA-183: pruebas de autorización y puerta de ejecución HTTP."""
from unittest.mock import Mock, patch
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from orchestrator.decision_flow import DecisionType, OrchestratorDecision
from ai_api.views import tool_calling


class KEFA183EndpointTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = Mock(pk=1, is_authenticated=True, is_active=True)
        self.user.get_all_permissions.return_value = {"users.kefa_tasks_write"}

    def post(self, data):
        request = self.factory.post('/api/ai/tool-calling/', data, format='json')
        force_authenticate(request, user=self.user)
        return tool_calling(request)

    @patch('ai_api.views.dispatch_prepared_call')
    @patch('ai_api.views.is_dispatch_enabled', return_value=False)
    @patch('ai_api.views.ToolCallingBridge')
    def test_disabled_allows_questions_but_not_actions(self, bridge, enabled, sender):
        bridge.return_value.procesar.return_value = [{
            'decision': OrchestratorDecision(DecisionType.RESPOND, reason='Hola'),
            'status': 'response', 'message': 'Hola',
        }]
        response = self.post({"mensaje": "¿Cómo puedo organizarme?", "ejecutar": True})
        self.assertEqual(response.status_code, 200)
        sender.assert_not_called()

        bridge.return_value.procesar.return_value = [{
            'decision': OrchestratorDecision(DecisionType.EXECUTE, 'tasks.create'),
            'status': 'prepared', 'payload': {'tool': 'tasks.create'},
        }]
        response = self.post({"mensaje": "Crea tarea", "ejecutar": True})
        self.assertEqual(response.status_code, 503)
        sender.assert_not_called()

    @patch('ai_api.views.dispatch_prepared_call')
    @patch('ai_api.views.is_dispatch_enabled', return_value=True)
    @patch('ai_api.views.ToolCallingBridge')
    def test_ambiguous_user_message_does_not_trigger_n8n(self, bridge, enabled, sender):
        bridge.return_value.procesar.return_value = [{
            'decision': OrchestratorDecision(DecisionType.EXECUTE, 'calendar.create_event'),
            'status': 'prepared', 'payload': {'tool': 'calendar.create_event'},
        }]
        response = self.post({"mensaje": "Tengo que estudiar mañana", "ejecutar": True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['resultados'][0]['decision'], 'respond')
        sender.assert_not_called()

    @patch('ai_api.views.dispatch_prepared_call')
    @patch('ai_api.views.is_dispatch_enabled', return_value=True)
    @patch('ai_api.views.ToolCallingBridge')
    def test_confused_task_and_event_stays_in_chat(self, bridge, enabled, sender):
        bridge.return_value.procesar.return_value = [{
            'decision': OrchestratorDecision(DecisionType.EXECUTE, 'calendar.create_event'),
            'status': 'prepared', 'payload': {'tool': 'calendar.create_event'},
        }]
        response = self.post({"mensaje": "Crea una tarea llamada examen", "ejecutar": True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['resultados'][0]['decision'], 'respond')
        sender.assert_not_called()

    @patch('ai_api.views.dispatch_prepared_call')
    @patch('ai_api.views.is_dispatch_enabled', return_value=True)
    @patch('ai_api.views.ToolCallingBridge')
    def test_explicit_execution_uses_server_permissions(self, bridge, enabled, sender):
        bridge.return_value.procesar.return_value = [{
            'decision': OrchestratorDecision(DecisionType.EXECUTE, 'tasks.create'),
            'status': 'prepared',
            'payload': {'tool': 'tasks.create', 'parameters': {'title': 'Compra'}}
        }]
        sender.return_value = {'status': 'accepted', 'http_status': 200}
        response = self.post({'mensaje': 'Crea tarea', 'ejecutar': True,
                              'granted_permissions': ['admin:all'], 'confirmed': True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['resultados'][0]['status'], 'accepted')
        sender.assert_called_once_with(bridge.return_value.procesar.return_value[0]['payload'],
                                       granted_permissions=['tasks:write'])
        bridge.return_value.procesar.assert_called_once_with(
            'Crea tarea', granted_permissions=['tasks:write'], confirmed=False, user_id='1')

    @patch('ai_api.views.dispatch_prepared_call')
    @patch('ai_api.views.is_dispatch_enabled', return_value=True)
    @patch('ai_api.views.ToolCallingBridge')
    def test_multiple_calls_do_not_execute(self, bridge, enabled, sender):
        one = {'decision': OrchestratorDecision(DecisionType.EXECUTE, 'tasks.create'),
               'status': 'prepared', 'payload': {'tool': 'tasks.create'}}
        bridge.return_value.procesar.return_value = [one, one]
        self.assertEqual(self.post({'mensaje': 'Dos tareas', 'ejecutar': True}).status_code, 409)
        sender.assert_not_called()

    @patch('ai_api.views.dispatch_prepared_call')
    @patch('ai_api.views.is_dispatch_enabled', return_value=True)
    @patch('ai_api.views.ToolCallingBridge')
    def test_pending_confirmation_does_not_execute(self, bridge, enabled, sender):
        bridge.return_value.procesar.return_value = [{
            'decision': OrchestratorDecision(DecisionType.REQUEST_CONFIRMATION, 'tasks.delete'),
            'status': 'not_prepared', 'request_id': 'abc'}]
        self.assertEqual(self.post({'mensaje': 'Eliminar tarea', 'ejecutar': True}).status_code, 409)
        sender.assert_not_called()

    @patch('ai_api.views.ToolCallingBridge')
    def test_bad_execute_type(self, bridge):
        self.assertEqual(self.post({'mensaje': 'Crea tarea', 'ejecutar': 'true'}).status_code, 400)
        bridge.assert_not_called()
