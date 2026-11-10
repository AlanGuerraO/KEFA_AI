
import unittest
from unittest.mock import MagicMock

from services.claude_service import ClaudeService


class TestClaudeService(unittest.TestCase):

    def test_mensaje_vacio(self):
        cliente_falso = MagicMock()
        servicio = ClaudeService(client=cliente_falso)

        with self.assertRaises(ValueError):
            servicio.enviar_mensaje("")

        cliente_falso.messages.create.assert_not_called()

    def test_enviar_mensaje(self):
        cliente_falso = MagicMock()
        cliente_falso.messages.create.return_value.content[0].text = (
            "Hola, soy Claude"
        )

        servicio = ClaudeService(client=cliente_falso)

        respuesta = servicio.enviar_mensaje("Hola")

        self.assertEqual(respuesta, "Hola, soy Claude")
        cliente_falso.messages.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
