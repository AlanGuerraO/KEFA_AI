
import unittest

from orchestrator.parameter_extractor import ParameterExtractor


class TestParameterExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = ParameterExtractor()

    def test_enviar_correo(self):
        result = self.extractor.extract(
            "Enviar correo a juan@gmail.com "
            "asunto: Reunión mensaje: Hola Juan",
            "enviar_correo"
        )

        self.assertEqual(
            result["parametros"]["destinatario"],
            "juan@gmail.com"
        )
        self.assertTrue(result["completo"])

    def test_informacion_faltante(self):
        result = self.extractor.extract(
            "Enviar correo a juan@gmail.com",
            "enviar_correo"
        )

        self.assertIn("asunto", result["faltantes"])
        self.assertIn("mensaje", result["faltantes"])
        self.assertFalse(result["completo"])

    def test_crear_evento(self):
        result = self.extractor.extract(
            "Crear evento: Reunión fecha: 2026-11-05 hora: 10:30",
            "crear_evento"
        )

        self.assertEqual(
            result["parametros"]["fecha"],
            "2026-11-05"
        )
        self.assertTrue(result["completo"])

    def test_crear_tarea(self):
        result = self.extractor.extract(
            "Crear tarea: Terminar proyecto KEFA",
            "crear_tarea"
        )

        self.assertEqual(
            result["parametros"]["titulo"],
            "Terminar proyecto KEFA"
        )
        self.assertTrue(result["completo"])

    def test_instruccion_vacia(self):
        with self.assertRaises(ValueError):
            self.extractor.extract("", "crear_tarea")

    def test_intencion_desconocida(self):
        result = self.extractor.extract(
            "Realizar una operación",
            "intencion_desconocida"
        )

        self.assertFalse(result["completo"])


if __name__ == "__main__":
    unittest.main()
