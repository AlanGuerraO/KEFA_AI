
import unittest
from unittest.mock import Mock

from orchestrator.instruction_processor import InstructionProcessor


class TestInstructionProcessor(unittest.TestCase):

    def setUp(self):
        self.claude = Mock()
        self.processor = InstructionProcessor(self.claude)

    def test_instruccion_valida(self):
        self.claude.enviar_mensaje.return_value = """
        {
            "intencion": "consultar_clima",
            "herramienta": null,
            "parametros": {"ciudad": "Oaxaca"},
            "informacion_faltante": [],
            "requiere_confirmacion": false,
            "estado": "analizado"
        }
        """

        resultado = self.processor.procesar_instruccion(
            "Consulta el clima en Oaxaca"
        )

        self.assertEqual(resultado["intencion"], "consultar_clima")
        self.assertEqual(resultado["parametros"]["ciudad"], "Oaxaca")
        self.claude.enviar_mensaje.assert_called_once()

    def test_instruccion_vacia(self):
        with self.assertRaises(ValueError):
            self.processor.procesar_instruccion("")

        self.claude.enviar_mensaje.assert_not_called()

    def test_respuesta_invalida(self):
        self.claude.enviar_mensaje.return_value = "No es JSON"

        with self.assertRaises(ValueError):
            self.processor.procesar_instruccion("Consulta el clima")

    def test_informacion_faltante(self):
        self.claude.enviar_mensaje.return_value = """
        {
            "intencion": "consultar_clima",
            "herramienta": null,
            "parametros": {},
            "informacion_faltante": ["ciudad"],
            "requiere_confirmacion": false,
            "estado": "analizado"
        }
        """

        resultado = self.processor.procesar_instruccion(
            "Consulta el clima"
        )

        self.assertIn("ciudad", resultado["informacion_faltante"])


if __name__ == "__main__":
    unittest.main()
