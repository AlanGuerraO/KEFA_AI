
import unittest
from unittest.mock import Mock

from orchestrator.tool_calling_bridge import ToolCallingBridge
from orchestrator.decision_flow import DecisionType


class TestToolCallingBridge(unittest.TestCase):

    def test_herramienta_preparada(self):
        servicio = Mock()
        servicio.procesar.return_value = [{
            "type": "tool_call",
            "status": "prepared",
            "payload": {
                "tool": "tasks.create",
                "parameters": {"title": "Entregar proyecto"},
                "execution": {"method": "n8n"},
            },
        }]

        puente = ToolCallingBridge(tool_service=servicio)

        resultado = puente.procesar(
            "Crea una tarea",
            granted_permissions=["tasks:write"],
        )

        self.assertEqual(len(resultado), 1)
        self.assertEqual(
            resultado[0]["decision"].decision,
            DecisionType.EXECUTE,
        )
        self.assertEqual(
            resultado[0]["status"], "prepared"
        )

    def test_confirmacion(self):
        servicio = Mock()
        servicio.procesar.return_value = [{
            "type": "error",
            "tool": "calendar.delete_event",
            "code": "ConfirmationRequiredError",
            "message": "Requiere confirmacion.",
        }]

        puente = ToolCallingBridge(tool_service=servicio)
        resultado = puente.procesar("Elimina mi evento")

        self.assertEqual(
            resultado[0]["decision"].decision,
            DecisionType.REQUEST_CONFIRMATION,
        )

    def test_rechazo(self):
        servicio = Mock()
        servicio.procesar.return_value = [{
            "type": "error",
            "tool": "herramienta_falsa",
            "code": "unknown_tool",
            "message": "Herramienta desconocida.",
        }]

        puente = ToolCallingBridge(tool_service=servicio)
        resultado = puente.procesar("Ejecuta herramienta falsa")

        self.assertEqual(
            resultado[0]["decision"].decision,
            DecisionType.REJECT,
        )


if __name__ == "__main__":
    unittest.main()
