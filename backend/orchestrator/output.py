from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class OrchestratorOutput:
    """
    Salida estándar generada por el orquestador de KEFA.
    """

    success: bool
    message: str
    action: Optional[str] = None
    tool: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    requires_confirmation: bool = False

    @classmethod
    def successful(
        cls,
        message: str,
        action: Optional[str] = None,
        tool: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> "OrchestratorOutput":
        return cls(
            success=True,
            message=message,
            action=action,
            tool=tool,
            data=data or {},
        )

    @classmethod
    def failed(
        cls,
        message: str,
        error: str,
    ) -> "OrchestratorOutput":
        return cls(
            success=False,
            message=message,
            error=error,
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la salida a un diccionario.
        """
        return {
            "success": self.success,
            "message": self.message,
            "action": self.action,
            "tool": self.tool,
            "data": self.data,
            "error": self.error,
            "requires_confirmation": self.requires_confirmation,
        }