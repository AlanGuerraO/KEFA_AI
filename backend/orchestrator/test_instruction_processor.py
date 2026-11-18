
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
    "intencion": "crear_tarea",
    "herramienta": "tasks.create",
    "parametros": {
        "title": "Comprar materiales"
    },
    "informacion_faltante": [],
    "requiere_confirmacion": false,
    "estado": "analizado",
    "mensaje": "Tarea preparada"
}
"""

        resultado = self.processor.procesar_instruccion(
            "Crea una tarea para comprar materiales"
        )

        self.assertEqual(
            resultado["intencion"],
            "crear_tarea"
        )
        self.assertEqual(
            resultado["herramienta"],
            "tasks.create"
        )
        self.assertEqual(
            resultado["parametros"]["title"],
            "Comprar materiales"
        )
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
    "intencion": "crear_tarea",
    "herramienta": "tasks.create",
    "parametros": {},
    "informacion_faltante": ["title"],
    "requiere_confirmacion": false,
    "estado": "incompleto",
    "mensaje": "¿Qué título tendrá la tarea?"
}
"""

        resultado = self.processor.procesar_instruccion(
            "Crea una tarea"
        )

        self.assertEqual(
            resultado["estado"],
            "incompleto"
        )
        self.assertIn(
            "title",
            resultado["informacion_faltante"]
        )
        self.assertEqual(
            resultado["mensaje"],
            "¿Qué título tendrá la tarea?"
        )



if __name__ == "__main__":
    unittest.main()
