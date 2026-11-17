
"""KEFA-017: validación de respuestas de confirmación."""

import hmac

from orchestrator.confirmation_store import ConfirmationStore


class ConfirmationValidator:
    def __init__(self, store: ConfirmationStore):
        self.store = store


    def validate(
        self,
        request_id: str,
        tool_name: str,
        parameters: dict,
        response: str,
        user_id: str,
    ) -> bool:
        """Valida la respuesta de un usuario autorizado."""

        if not isinstance(user_id, str) or not user_id.strip():
            return False

        request = self.store.get(request_id)

        if request is None:
            return False

        if not isinstance(tool_name, str):
            return False

        if not hmac.compare_digest(request.tool_name, tool_name):
            return False

        if not isinstance(parameters, dict):
            return False

        if request.parameters != parameters:
            return False

        if not isinstance(response, str):
            return False

        decision = response.strip().lower()

        if decision not in ("confirmar", "rechazar", "cancelar"):
            return False

        consumed = self.store.consume(
    request_id,
    user_id,
    tool_name,
    parameters,
)

        if consumed is None:
            return False

        if decision in ("rechazar", "cancelar"):
            return False

        return True







