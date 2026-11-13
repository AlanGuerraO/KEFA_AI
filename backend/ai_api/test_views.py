
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient


class TestToolCallingEndpoint(SimpleTestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/ai/tool-calling/"

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
        from rest_framework.test import APIRequestFactory, force_authenticate
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

        usuario = type(
            "UsuarioPrueba",
            (),
            {"is_authenticated": True, "is_active": True}
        )()

        force_authenticate(request, user=usuario)

        bridge_mock.return_value.procesar.return_value = []

        response = tool_calling(request)

        self.assertEqual(response.status_code, 200)

        bridge_mock.return_value.procesar.assert_called_once_with(
            "Crea una tarea",
            granted_permissions=[],
            confirmed=False,
        )

    @patch("ai_api.views.ToolCallingBridge")
    def test_mensaje_vacio(self, bridge_mock):
        from rest_framework.test import APIRequestFactory, force_authenticate
        from ai_api.views import tool_calling

        request = APIRequestFactory().post(
            self.url,
            {"mensaje": ""},
            format="json",
        )

        usuario = type(
            "UsuarioPrueba",
            (),
            {"is_authenticated": True, "is_active": True}
        )()

        force_authenticate(request, user=usuario)

        response = tool_calling(request)

        self.assertEqual(response.status_code, 400)
        bridge_mock.assert_not_called()
