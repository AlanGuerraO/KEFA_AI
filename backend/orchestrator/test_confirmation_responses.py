
"""KEFA-017: pruebas de rechazo y cancelación."""

import unittest

from orchestrator.confirmation_request import create_confirmation_request
from orchestrator.confirmation_store import ConfirmationStore
from orchestrator.confirmation_validator import ConfirmationValidator


class TestConfirmationResponses(unittest.TestCase):

    def setUp(self):
        self.store = ConfirmationStore()
        self.validator = ConfirmationValidator(self.store)

        self.request = create_confirmation_request(
            "calendar.delete_event",
            {"event_id": "evento_123"},
        )
        self.store.save(self.request, user_id="usuario_1")

    def test_rechazo(self):
        result = self.validator.validate(
            self.request.request_id,
            "calendar.delete_event",
            {"event_id": "evento_123"},
            "rechazar",user_id="usuario_1"
        )

        self.assertFalse(result)

    def test_cancelacion(self):
        result = self.validator.validate(
            self.request.request_id,
            "calendar.delete_event",
            {"event_id": "evento_123"},
            "cancelar",user_id="usuario_1"
        )

        self.assertFalse(result)

    def test_confirmacion_valida(self):
        result = self.validator.validate(
            self.request.request_id,
            "calendar.delete_event",
            {"event_id": "evento_123"},
            "confirmar",user_id="usuario_1"
        )

        self.assertTrue(result)
        self.assertIsNone(
            self.store.get(self.request.request_id)
        )

    def test_no_reutilizar_confirmacion(self):
       
        args = (
            self.request.request_id,
            "calendar.delete_event",
            {"event_id": "evento_123"},
            "confirmar",
            "usuario_1",
        )


        self.assertTrue(self.validator.validate(*args))
        self.assertFalse(self.validator.validate(*args))


    def test_rechazo_cierra_solicitud(self):
        result = self.validator.validate(
            self.request.request_id,
            "calendar.delete_event",
            {"event_id": "evento_123"},
            "rechazar",user_id="usuario_1"
        )

        self.assertFalse(result)
        self.assertIsNone(
            self.store.get(self.request.request_id)
        )

    def test_cancelacion_cierra_solicitud(self):
        result = self.validator.validate(
            self.request.request_id,
            "calendar.delete_event",
            {"event_id": "evento_123"},
            "cancelar",user_id="usuario_1"
        )

        self.assertFalse(result)
        self.assertIsNone(
            self.store.get(self.request.request_id)
        )


    def test_otro_usuario_no_puede_confirmar(self):
        resultado = self.validator.validate(
            self.request.request_id,
            "calendar.delete_event",
            {"event_id": "evento_123"},
            "confirmar",
            user_id="usuario_2",
        )

        self.assertFalse(resultado)

        self.assertIsNotNone(
            self.store.get(self.request.request_id)
        )




if __name__ == "__main__":
    unittest.main()
