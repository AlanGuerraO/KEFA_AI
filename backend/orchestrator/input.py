from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class OrchestratorInput:
    """
    Entrada que recibe el orquestador de KEFA.
    """

    user_id: str
    message: str
    session_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """
        Valida los datos mínimos necesarios para procesar la solicitud.
        """
        if not self.user_id or not self.user_id.strip():
            raise ValueError("user_id es obligatorio")

        if not self.message or not self.message.strip():
            raise ValueError("message es obligatorio")

        if not isinstance(self.context, dict):
            raise ValueError("context debe ser un diccionario")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la entrada a un diccionario.
        """
        return {
            "user_id": self.user_id,
            "message": self.message,
            "session_id": self.session_id,
            "context": self.context,
        }