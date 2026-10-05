from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class OrchestratorError:
    """
    Representa un error controlado dentro del orquestador.
    """

    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorHandler:
    """
    Centraliza el manejo de errores del orquestador.
    """

    ERROR_MESSAGES = {
        "INVALID_INPUT": "La entrada recibida no es válida.",
        "TOOL_NOT_FOUND": "La herramienta solicitada no existe.",
        "INVALID_PARAMETERS": "Los parámetros de la herramienta no son válidos.",
        "PERMISSION_DENIED": "El usuario no tiene permisos suficientes.",
        "CONFIRMATION_REQUIRED": "La acción requiere confirmación del usuario.",
        "EXECUTION_ERROR": "Ocurrió un error al ejecutar la herramienta.",
        "INTERNAL_ERROR": "Ocurrió un error interno en el orquestador.",
    }

    @classmethod
    def create(
        cls,
        code: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> OrchestratorError:
        """
        Crea un error controlado.
        """

        final_message = message or cls.ERROR_MESSAGES.get(
            code,
            "Ocurrió un error desconocido.",
        )

        return OrchestratorError(
            code=code,
            message=final_message,
            details=details,
        )

    @classmethod
    def from_exception(
        cls,
        exception: Exception,
        code: str = "INTERNAL_ERROR",
    ) -> OrchestratorError:
        """
        Convierte una excepción en un error controlado sin
        exponer información sensible.
        """

        return cls.create(
            code=code,
            details={
                "exception_type": type(exception).__name__,
            },
        )

    @staticmethod
    def to_dict(error: OrchestratorError) -> Dict[str, Any]:
        """
        Convierte el error a un diccionario para poder
        devolverlo en la respuesta del orquestador.
        """

        return {
            "code": error.code,
            "message": error.message,
            "details": error.details or {},
        }