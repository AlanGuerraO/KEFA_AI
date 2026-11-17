
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from orchestrator.confirmation_request import create_confirmation_request
from orchestrator.confirmation_store import ConfirmationStore


class TestConfirmationConcurrency(unittest.TestCase):

    def test_solo_una_confirmacion_puede_consumirse(self):
        store = ConfirmationStore()

        request = create_confirmation_request(
            "calendar.delete_event",
            {"event_id": "evento_123"},
        )

        store.save(request, user_id="usuario_1")

        barrier = Barrier(2)

        def intentar_confirmar():
            barrier.wait()

            return store.consume(
                request.request_id,
                "usuario_1",
                "calendar.delete_event",
                {"event_id": "evento_123"},
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            resultados = list(
                executor.map(lambda _: intentar_confirmar(), range(2))
            )

        exitos = sum(resultado is not None for resultado in resultados)

        self.assertEqual(exitos, 1)
        self.assertIsNone(store.get(request.request_id))


if __name__ == "__main__":
    unittest.main()
