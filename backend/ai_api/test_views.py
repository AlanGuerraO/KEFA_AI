
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import (
    APIClient,
    APIRequestFactory,
    force_authenticate,
)

from orchestrator.decision_flow import (
    DecisionType,
    OrchestratorDecision,
)


class TestToolCallingEndpoint(SimpleTestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/ai/tool-calling/"
        self.confirmacion_url = "/api/ai/confirmar-accion/"

    def crear_usuario(self):
        return type(
            "UsuarioPrueba",
            (),
            {
                "pk": 1,
                "is_authenticated": True,
                "is_active": True,
            },
        )()

    def test_requiere_autenticacion(self):
        response = self.client.post(
            self.url,
            {"mensaje": "Crea una tarea"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    @patch("ai_api.views.ToolCallingBridge")
    def test_no_procesa_sin_autenticacion(self, bridge_mock):
        response = self.client.post(
            self.url,
            {"mensaje": "Elimina todos mis eventos"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)
        bridge_mock.assert_not_called()

    @patch("ai_api.views.ToolCallingBridge")
    def test_no_acepta_permisos_del_cliente(self, bridge_mock):
        from ai_api.views import tool_calling

        request = APIRequestFactory().post(
            self.url,
            {
                "mensaje": "Crea una tarea",
                "granted_permissions": ["tasks:write"],
                "confirmed": True,
            },
            format="json",
        )

        force_authenticate(request, user=self.crear_usuario())
        bridge_mock.return_value.procesar.return_value = []

        response = tool_calling(request)

        self.assertEqual(response.status_code, 200)

        bridge_mock.return_value.procesar.assert_called_once_with(
            "Crea una tarea",
            granted_permissions=[],
            confirmed=False,
            user_id="1",
        )

    @patch("ai_api.views.ToolCallingBridge")
    def test_mensaje_vacio(self, bridge_mock):
        from ai_api.views import tool_calling

        request = APIRequestFactory().post(
            self.url,
            {"mensaje": ""},
            format="json",
        )

        force_authenticate(request, user=self.crear_usuario())

        response = tool_calling(request)

        self.assertEqual(response.status_code, 400)
        bridge_mock.assert_not_called()

    @patch("ai_api.views.ToolCallingBridge")
    def test_devuelve_request_id_confirmacion(self, bridge_mock):
        from ai_api.views import tool_calling

        request = APIRequestFactory().post(
            self.url,
            {"mensaje": "Elimina mi evento"},
            format="json",
        )

        force_authenticate(request, user=self.crear_usuario())

        decision = OrchestratorDecision(
            decision=DecisionType.REQUEST_CONFIRMATION,
            tool_name="calendar.delete_event",
            reason="La operación requiere confirmación.",
        )

        bridge_mock.return_value.procesar.return_value = [
            {
                "decision": decision,
                "status": "not_prepared",
                "request_id": "solicitud_prueba_123",
            }
        ]

        response = tool_calling(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["resultados"]), 1)

        resultado = response.data["resultados"][0]

        self.assertEqual(
            resultado["decision"],
            "request_confirmation",
        )

        self.assertEqual(
            resultado["tool"],
            "calendar.delete_event",
        )

        self.assertEqual(
            resultado["request_id"],
            "solicitud_prueba_123",
        )

        self.assertEqual(
            resultado["status"],
            "not_prepared",
        )

        bridge_mock.return_value.procesar.assert_called_once_with(
            "Elimina mi evento",
            granted_permissions=[],
            confirmed=False,
            user_id="1",
        )

    # ======================================
    # KEFA-017: PRUEBAS DE CONFIRMACION
    # ======================================

    def test_confirmacion_requiere_autenticacion(self):
        response = self.client.post(
            self.confirmacion_url,
            {
                "request_id": "solicitud_prueba_123",
                "respuesta": "confirmar",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_confirmacion_sin_request_id(self):
        from ai_api.views import confirmar_accion

        request = APIRequestFactory().post(
            self.confirmacion_url,
            {"respuesta": "confirmar"},
            format="json",
        )

        force_authenticate(request, user=self.crear_usuario())

        response = confirmar_accion(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_confirmacion_respuesta_invalida(self):
        from ai_api.views import confirmar_accion

        request = APIRequestFactory().post(
            self.confirmacion_url,
            {
                "request_id": "solicitud_prueba_123",
                "respuesta": "ejecutar_sin_confirmacion",
            },
            format="json",
        )

        force_authenticate(request, user=self.crear_usuario())

        response = confirmar_accion(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_confirmacion_no_habilita_ejecucion(self):
        from ai_api.views import confirmar_accion

        request = APIRequestFactory().post(
            self.confirmacion_url,
            {
                "request_id": "solicitud_prueba_123",
                "respuesta": "confirmar",
            },
            format="json",
        )

        force_authenticate(request, user=self.crear_usuario())

        response = confirmar_accion(request)

        # La confirmacion aun no esta habilitada.
        # No debe ejecutar operaciones sensibles.
        self.assertEqual(response.status_code, 501)
        self.assertIn("error", response.data)
