
import unittest

from orchestrator.output import OrchestratorOutput


class TestResponses(unittest.TestCase):

    def test_respuesta_exitosa(self):
        respuesta = OrchestratorOutput.successful(
            message="Tarea creada correctamente",
            action="create",
            tool="tasks.create",
            data={"id": 1}
        )

        resultado = respuesta.to_dict()

        self.assertTrue(resultado["success"])
        self.assertEqual(
            resultado["message"],
            "Tarea creada correctamente"
        )
        self.assertEqual(resultado["action"], "create")
        self.assertEqual(resultado["tool"], "tasks.create")
        self.assertEqual(resultado["data"], {"id": 1})

    def test_respuesta_error(self):
        respuesta = OrchestratorOutput.failed(
            message="No se pudo crear la tarea",
            error="VALIDATION_ERROR"
        )

        resultado = respuesta.to_dict()

        self.assertFalse(resultado["success"])
        self.assertEqual(
            resultado["error"],
            "VALIDATION_ERROR"
        )
        self.assertEqual(
            resultado["message"],
            "No se pudo crear la tarea"
        )

    def test_respuesta_sin_datos(self):
        respuesta = OrchestratorOutput.successful(
            message="Operacion completada"
        )

        resultado = respuesta.to_dict()

        self.assertTrue(resultado["success"])
        self.assertEqual(resultado["data"], {})
        self.assertIsNone(resultado["action"])
        self.assertIsNone(resultado["tool"])

    def test_respuesta_con_confirmacion(self):
        respuesta = OrchestratorOutput(
            success=True,
            message="Se requiere confirmacion",
            action="delete",
            tool="tasks.delete",
            requires_confirmation=True
        )

        resultado = respuesta.to_dict()

        self.assertTrue(
            resultado["requires_confirmation"]
        )
        self.assertEqual(resultado["action"], "delete")

    def test_respuesta_con_datos(self):
        datos = {
            "id": 10,
            "title": "Estudiar Python",
            "status": "pending"
        }

        respuesta = OrchestratorOutput.successful(
            message="Consulta exitosa",
            action="read",
            tool="tasks.read",
            data=datos
        )

        resultado = respuesta.to_dict()

        self.assertEqual(resultado["data"], datos)
        self.assertEqual(
            resultado["data"]["title"],
            "Estudiar Python"
        )

    def test_estructura_respuesta(self):
        respuesta = OrchestratorOutput.successful(
            message="Respuesta de prueba"
        )

        resultado = respuesta.to_dict()

        campos = [
            "success",
            "message",
            "action",
            "tool",
            "data",
            "error",
            "requires_confirmation"
        ]

        for campo in campos:
            self.assertIn(campo, resultado)


if __name__ == "__main__":
    unittest.main()
