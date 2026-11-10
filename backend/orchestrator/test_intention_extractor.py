
import unittest

from orchestrator.intention_extractor import IntentionExtractor


class TestIntentionExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = IntentionExtractor()

    def test_enviar_correo(self):
        resultado = self.extractor.extraer("Enviar correo a Juan")
        self.assertEqual(resultado["intencion"], "enviar_correo")

    def test_crear_tarea(self):
        resultado = self.extractor.extraer("Crear tarea de matemáticas")
        self.assertEqual(resultado["intencion"], "crear_tarea")

    def test_crear_evento(self):
        resultado = self.extractor.extraer("Agendar reunión mañana")
        self.assertEqual(resultado["intencion"], "crear_evento")

    def test_instruccion_vacia(self):
        resultado = self.extractor.extraer("")
        self.assertTrue(resultado["requiere_aclaracion"])

    def test_intencion_desconocida(self):
        resultado = self.extractor.extraer("Hola, buenos días")
        self.assertEqual(resultado["intencion"], "desconocida")


if __name__ == "__main__":
    unittest.main()
