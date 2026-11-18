
import unittest
from unittest.mock import Mock

from orchestrator.tool_calling_bridge import ToolCallingBridge
from orchestrator.decision_flow import DecisionType
from orchestrator.confirmation_store import confirmation_store


class TestToolCallingBridge(unittest.TestCase):

    def test_herramienta_preparada_se_envia_a_n8n(self):
        servicio = Mock()
        servicio.procesar.return_value = [{
            "type": "tool_call",
            "payload": {
                "tool": "tasks.create",
                "parameters": {"title": "Tarea de prueba"},
                "execution": {"method": "n8n", "status": "cataloged"},
            },
        }]

        ejecutor = Mock(return_value={
            "status": "accepted",
            "http_status": 200,
            "response": '{"message":"Workflow was started"}',
        })

        puente = ToolCallingBridge(
            tool_service=servicio,
            n8n_executor=ejecutor,
        )

        resultado = puente.procesar("Crea una tarea")

        self.assertEqual(len(resultado), 1)
        self.assertEqual(
            resultado[0]["decision"].decision,
            DecisionType.EXECUTE,
        )
        self.assertEqual(resultado[0]["status"], "accepted")
        self.assertEqual(
            resultado[0]["execution_result"]["http_status"],
            200,
        )
        ejecutor.assert_called_once_with(
            servicio.procesar.return_value[0]["payload"]
        )

    def test_error_de_n8n_se_propaga(self):
        servicio = Mock()
        servicio.procesar.return_value = [{
            "type": "tool_call",
            "payload": {
                "tool": "tasks.create",
                "parameters": {"title": "Tarea de prueba"},
                "execution": {"method": "n8n", "status": "cataloged"},
            },
        }]

        ejecutor = Mock(side_effect=RuntimeError("Error de conexión"))

        puente = ToolCallingBridge(
            tool_service=servicio,
            n8n_executor=ejecutor,
        )

        with self.assertRaisesRegex(RuntimeError, "Error de conexión"):
            puente.procesar("Crea una tarea")

    def test_confirmacion_no_ejecuta_n8n(self):
        servicio = Mock()
        servicio.procesar.return_value = [{
            "type": "error",
            "tool": "calendar.delete_event",
            "parameters": {"event_id": "evento_123"},
            "code": "ConfirmationRequiredError",
            "message": "Requiere confirmacion.",
        }]

        ejecutor = Mock()
        puente = ToolCallingBridge(
            tool_service=servicio,
            n8n_executor=ejecutor,
        )

        resultado = puente.procesar(
            "Elimina mi evento",
            user_id="usuario_prueba_1",
        )

        self.assertEqual(len(resultado), 1)
        self.assertEqual(
            resultado[0]["decision"].decision,
            DecisionType.REQUEST_CONFIRMATION,
        )
        ejecutor.assert_not_called()

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

    def test_rechazo_no_ejecuta_n8n(self):
        servicio = Mock()
        servicio.procesar.return_value = [{
            "type": "error",
            "tool": "herramienta_falsa",
            "code": "UnknownToolError",
            "message": "Herramienta desconocida.",
        }]

        ejecutor = Mock()
        puente = ToolCallingBridge(
            tool_service=servicio,
            n8n_executor=ejecutor,
        )

        resultado = puente.procesar("Ejecuta herramienta falsa")

        self.assertEqual(len(resultado), 1)
        self.assertEqual(
            resultado[0]["decision"].decision,
            DecisionType.REJECT,
        )
        ejecutor.assert_not_called()


if __name__ == "__main__":
    unittest.main()
