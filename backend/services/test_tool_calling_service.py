
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from services.tool_calling_service import (
    ToolCallingService,
    build_claude_tools,
)


class TestToolCallingService(unittest.TestCase):

    def fake_client(self, name, parameters):
        client = Mock()
        block = SimpleNamespace(
            type="tool_use",
            id="toolu_test",
            name=name,
            input=parameters,
        )
        client.messages.create.return_value = (
            SimpleNamespace(content=[block])
        )
        return client

    def test_schema(self):
        tools, name_map = build_claude_tools()
        self.assertTrue(tools)
        self.assertIn("tasks__create", name_map)

    def test_herramienta_valida(self):
        client = self.fake_client(
            "tasks__create",
            {"title": "Entregar proyecto"},
        )
        service = ToolCallingService(client=client)

        result = service.procesar(
            "Crea una tarea para entregar el proyecto",
            granted_permissions=["tasks:write"],
        )
        self.assertEqual(result[0]["type"], "tool_call")
        self.assertEqual(result[0]["status"], "prepared")

    def test_herramienta_desconocida(self):
        client = self.fake_client("herramienta_falsa", {})
        service = ToolCallingService(client=client)

        result = service.procesar("Ejecuta herramienta falsa")
        self.assertEqual(result[0]["code"], "unknown_tool")

    def test_parametros_incompletos(self):
        client = self.fake_client("tasks__create", {})
        service = ToolCallingService(client=client)

        result = service.procesar(
            "Crea una tarea",
            granted_permissions=["tasks:write"],
        )
        self.assertEqual(result[0]["type"], "error")

    def test_sin_permisos(self):
        client = self.fake_client(
            "tasks__create",
            {"title": "Entregar proyecto"},
        )
        service = ToolCallingService(client=client)

        result = service.procesar(
            "Crea una tarea",
            granted_permissions=[],
        )
        self.assertEqual(
            result[0]["code"], "PermissionDeniedError"
        )

    def test_mensaje_vacio(self):
        service = ToolCallingService(client=Mock())
        with self.assertRaises(ValueError):
            service.procesar("")
    def test_confirmacion_requerida(self):
        client = self.fake_client(
            "calendar__delete_event",
            {"event_id": "evento_123"},
        )

        service = ToolCallingService(client=client)

        result = service.procesar(
            "Elimina el evento del calendario",
            granted_permissions=["calendar:write"],
            confirmed=False,
        )

        self.assertEqual(result[0]["type"], "error")
        self.assertEqual(
            result[0]["code"],
            "ConfirmationRequiredError"
        )
    def test_multiples_herramientas(self):
        client = Mock()

        bloques = [
            SimpleNamespace(
                type="tool_use",
                id="toolu_001",
                name="tasks__create",
                input={"title": "Entregar proyecto"},
            ),
            SimpleNamespace(
                type="tool_use",
                id="toolu_002",
                name="tasks__create",
                input={"title": "Estudiar matemáticas"},
            ),
        ]
    def test_error_claude(self):
        client = Mock()
        client.messages.create.side_effect = ConnectionError(
            "No se pudo conectar con Claude"
        )

        service = ToolCallingService(client=client)

        result = service.procesar(
            "Crea una tarea",
            granted_permissions=["tasks:write"],
        )

        self.assertEqual(result[0]["type"], "error")
        self.assertEqual(result[0]["code"], "claude_api_error")

if __name__ == "__main__":
    unittest.main()