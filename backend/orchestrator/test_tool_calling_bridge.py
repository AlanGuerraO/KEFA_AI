
import unittest
from unittest.mock import Mock

from orchestrator.tool_calling_bridge import ToolCallingBridge
from orchestrator.decision_flow import DecisionType
from orchestrator.confirmation_store import confirmation_store


class TestToolCallingBridge(unittest.TestCase):

    
    def test_herramienta_preparada(self):
        servicio = Mock()
        servicio.procesar.return_value = [{
            "type": "tool_call",
            "payload": {
                "tool": "tasks.create_task",
                "parameters": {"title": "Tarea de prueba"},
            },
        }]

        puente = ToolCallingBridge(tool_service=servicio)

        resultado = puente.procesar("Crea una tarea")

        self.assertEqual(len(resultado), 1)
        self.assertEqual(
            resultado[0]["decision"].decision,
            DecisionType.EXECUTE,
        )
        self.assertEqual(resultado[0]["status"], "prepared")

    def test_confirmacion(self):
        servicio = Mock()
        servicio.procesar.return_value = [{
            "type": "error",
            "tool": "calendar.delete_event",
            "parameters": {"event_id": "evento_123"},
            "code": "ConfirmationRequiredError",
            "message": "Requiere confirmacion.",
        }]

        puente = ToolCallingBridge(tool_service=servicio)

        resultado = puente.procesar(
            "Elimina mi evento",
            user_id="usuario_prueba_1",
        )

        self.assertEqual(len(resultado), 1)
        self.assertEqual(
            resultado[0]["decision"].decision,
            DecisionType.REQUEST_CONFIRMATION,
        )

        request_id = resultado[0]["request_id"]
        self.assertIsInstance(request_id, str)
        self.assertTrue(request_id)

        solicitud = confirmation_store.get(request_id)
        self.assertIsNotNone(solicitud)
        self.assertEqual(
            solicitud.tool_name,
            "calendar.delete_event",
        )
        self.assertEqual(
            solicitud.parameters,
            {"event_id": "evento_123"},
        )

    def test_rechazo(self):
        servicio = Mock()
        servicio.procesar.return_value = [{
            "type": "error",
            "tool": "herramienta_falsa",
            "code": "UnknownToolError",
            "message": "Herramienta desconocida.",
        }]

        puente = ToolCallingBridge(tool_service=servicio)

        resultado = puente.procesar("Ejecuta herramienta falsa")

        self.assertEqual(len(resultado), 1)
        self.assertEqual(
            resultado[0]["decision"].decision,
            DecisionType.REJECT,
        )

