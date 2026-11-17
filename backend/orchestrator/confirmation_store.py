
"""KEFA-017: almacenamiento temporal de confirmaciones."""

from datetime import datetime, timedelta, timezone

from threading import Lock

from orchestrator.confirmation_request import ConfirmationRequest


class ConfirmationStore:
    """Mantiene solicitudes pendientes durante su vigencia."""

 
    def __init__(self):
        self._pending = {}
        self._lock = Lock()


    def save(self, request: ConfirmationRequest, user_id: str = None):
        if not isinstance(request, ConfirmationRequest):
            raise ValueError("Solicitud de confirmación inválida.")

        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("El identificador del usuario es obligatorio.")

        with self._lock:
            if request.request_id in self._pending:
                raise ValueError("La solicitud ya está registrada.")

            self._pending[request.request_id] = {
                "request": request,
                "user_id": user_id,
                "expires_at": (
                    datetime.now(timezone.utc)
                    + timedelta(minutes=5)
                ),
            }


    def get(self, request_id: str):
        entry = self._pending.get(request_id)

        if entry is None:
            return None

        if datetime.now(timezone.utc) >= entry["expires_at"]:
            del self._pending[request_id]
            return None

        return entry["request"]

    def remove(self, request_id: str):
        return self._pending.pop(request_id, None) is not None


    
    def consume(
        self,
        request_id: str,
        user_id: str,
        tool_name: str = None,
        parameters: dict = None,
    ):
        """Valida y consume una solicitud de forma atómica."""

        with self._lock:
            entry = self._pending.get(request_id)

            if entry is None:
                return None

            if entry["user_id"] != user_id:
                return None

            if datetime.now(timezone.utc) >= entry["expires_at"]:
                del self._pending[request_id]
                return None

            request = entry["request"]

            if tool_name is None or parameters is None:
                return None

            if request.tool_name != tool_name:
                return None

            if not isinstance(parameters, dict):
                return None

            if request.parameters != parameters:
                return None

            del self._pending[request_id]
            return request

        
confirmation_store = ConfirmationStore()

