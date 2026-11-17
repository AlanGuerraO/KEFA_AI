
"""KEFA-017: registro de decisiones de confirmación."""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ConfirmationLogEntry:
    request_id: str
    user_id: str
    tool_name: str
    decision: str
    timestamp: str


class ConfirmationLog:
    def __init__(self):
        self._entries = []

    def record(
        self,
        request_id: str,
        user_id: str,
        tool_name: str,
        decision: str,
    ) -> ConfirmationLogEntry:

        if decision not in ("confirmed", "rejected", "cancelled"):
            raise ValueError("Decisión de confirmación inválida.")

        if not all(
            isinstance(value, str) and value.strip()
            for value in (request_id, user_id, tool_name)
        ):
            raise ValueError("Los identificadores son obligatorios.")

        entry = ConfirmationLogEntry(
            request_id=request_id,
            user_id=user_id,
            tool_name=tool_name,
            decision=decision,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        self._entries.append(entry)
        return entry

    def list_entries(self):
        return list(self._entries)
