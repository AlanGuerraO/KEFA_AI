
import unittest
from unittest.mock import patch

from orchestrator.confirmation_request import ConfirmationRequest
from orchestrator.confirmation_store import ConfirmationStore
from orchestrator.confirmed_action import (
    InvalidConfirmationError,
    prepare_confirmed_action,
)


class TestConfirmedAction(unittest.TestCase):

    def setUp(self):
        self.store = ConfirmationStore()

        self.solicitud = ConfirmationRequest(
            request_id="solicitud_123",
            tool_name="calendar.delete_event",
            parameters={"event_id": "evento_123"},
            risk_level="high",
            message="Confirmar eliminación",
        )

        self.store.save(
            self.solicitud,
            user_id="usuario_1",
        )

        self.store_patch = patch(
            "orchestrator.confirmed_action.confirmation_store",
            self.store,
        )
        self.store_patch.start()
        self.addCleanup(self.store_patch.stop)

    @patch("orchestrator.confirmed_action.prepare_tool_call")
    def test_usuario_correcto(self, preparar_mock):
        preparar_mock.return_value = {
            "tool": "calendar.delete_event",
            "parameters": {"event_id": "evento_123"},
        }

        resultado = prepare_confirmed_action(
            "solicitud_123",
            "usuario_1",
            granted_permissions=["calendar:delete"],
        )

        self.assertEqual(
            resultado["tool"],
            "calendar.delete_event",
        )
        self.assertIsNone(self.store.get("solicitud_123"))

    @patch("orchestrator.confirmed_action.prepare_tool_call")
    def test_otro_usuario_no_puede_confirmar(self, preparar_mock):
        preparar_mock.return_value = {"tool": "calendar.delete_event"}

        with self.assertRaises(InvalidConfirmationError):
            prepare_confirmed_action(
                "solicitud_123",
                "usuario_2",
                granted_permissions=["calendar:delete"],
            )

        self.assertIsNotNone(self.store.get("solicitud_123"))

    @patch("orchestrator.confirmed_action.prepare_tool_call")
    def test_no_reutilizar_confirmacion(self, preparar_mock):
        preparar_mock.return_value = {"tool": "calendar.delete_event"}

        prepare_confirmed_action(
            "solicitud_123",
            "usuario_1",
            granted_permissions=["calendar:delete"],
        )

        with self.assertRaises(InvalidConfirmationError):
            prepare_confirmed_action(
                "solicitud_123",
                "usuario_1",
                granted_permissions=["calendar:delete"],
            )

    @patch("orchestrator.confirmed_action.prepare_tool_call")
    def test_permisos_insuficientes_no_consumen(self, preparar_mock):
        preparar_mock.side_effect = PermissionError(
            "Permisos insuficientes."
        )

        with self.assertRaises(PermissionError):
            prepare_confirmed_action(
                "solicitud_123",
                "usuario_1",
                granted_permissions=[],
            )

        self.assertIsNotNone(self.store.get("solicitud_123"))
