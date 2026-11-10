
import unittest

from orchestrator.error_handler import ErrorHandler, OrchestratorError


class TestErrorHandler(unittest.TestCase):

    def test_error_entrada_invalida(self):
        error = ErrorHandler.create("INVALID_INPUT")

        self.assertEqual(error.code, "INVALID_INPUT")
        self.assertIsInstance(error.message, str)
        self.assertTrue(error.message)

    def test_herramienta_no_encontrada(self):
        error = ErrorHandler.create("TOOL_NOT_FOUND")

        self.assertEqual(error.code, "TOOL_NOT_FOUND")
        self.assertTrue(error.message)

    def test_parametros_invalidos(self):
        error = ErrorHandler.create(
            "INVALID_PARAMETERS",
            details={"field": "title"}
        )

        self.assertEqual(error.code, "INVALID_PARAMETERS")
        self.assertEqual(error.details["field"], "title")

    def test_permisos_insuficientes(self):
        error = ErrorHandler.create("PERMISSION_DENIED")

        self.assertEqual(error.code, "PERMISSION_DENIED")
        self.assertTrue(error.message)

    def test_confirmacion_requerida(self):
        error = ErrorHandler.create("CONFIRMATION_REQUIRED")

        self.assertEqual(error.code, "CONFIRMATION_REQUIRED")

    def test_error_ejecucion(self):
        error = ErrorHandler.create("EXECUTION_ERROR")

        self.assertEqual(error.code, "EXECUTION_ERROR")

    def test_error_interno(self):
        error = ErrorHandler.create("INTERNAL_ERROR")

        self.assertEqual(error.code, "INTERNAL_ERROR")

    def test_error_desconocido(self):
        error = ErrorHandler.create("UNKNOWN_ERROR")

        self.assertEqual(error.code, "UNKNOWN_ERROR")
        self.assertTrue(error.message)

    def test_convertir_excepcion(self):
        exception = ValueError("Dato privado de prueba")

        error = ErrorHandler.from_exception(exception)

        self.assertIsInstance(error, OrchestratorError)
        self.assertEqual(error.code, "INTERNAL_ERROR")
        self.assertNotIn("Dato privado", error.message)

    def test_convertir_a_diccionario(self):
        error = ErrorHandler.create(
            "INVALID_INPUT",
            details={"field": "message"}
        )

        result = ErrorHandler.to_dict(error)

        self.assertEqual(result["code"], "INVALID_INPUT")
        self.assertIn("message", result)
        self.assertEqual(result["details"]["field"], "message")


if __name__ == "__main__":
    unittest.main()
