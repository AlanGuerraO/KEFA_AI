from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class ActionRecord:
    """
    Representa una acción procesada por el orquestador.
    """

    user_id: str
    action: str
    tool_name: Optional[str] = None
    status: str = "pending"
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ActionLogger:
    """
    Registra las acciones realizadas por el orquestador.

    No se deben guardar contraseñas, tokens ni credenciales.
    """

    def __init__(self) -> None:
        self._records: List[ActionRecord] = []

    def log(
        self,
        user_id: str,
        action: str,
        tool_name: Optional[str] = None,
        status: str = "pending",
        details: Optional[Dict[str, Any]] = None,
    ) -> ActionRecord:

        record = ActionRecord(
            user_id=user_id,
            action=action,
            tool_name=tool_name,
            status=status,
            details=details or {},
        )

        self._records.append(record)

        return record

    def get_records(self) -> List[Dict[str, Any]]:
        """
        Devuelve el historial de acciones.
        """

        return [
            asdict(record)
            for record in self._records
        ]

    def clear(self) -> None:
        """
        Limpia el historial almacenado en memoria.
        """

        self._records.clear()