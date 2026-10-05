from dataclasses import dataclass
from typing import Optional


@dataclass
class ConfirmationResult:
    """
    Resultado de la validación de confirmación.
    """

    allowed: bool
    requires_confirmation: bool
    message: Optional[str] = None


class ConfirmationManager:
    """
    Controla las confirmaciones requeridas antes de ejecutar
    acciones sensibles.
    """

    @staticmethod
    def check(
        requires_confirmation: bool,
        confirmed: bool,
        tool_name: Optional[str] = None,
    ) -> ConfirmationResult:

        # La herramienta no necesita confirmación
        if not requires_confirmation:
            return ConfirmationResult(
                allowed=True,
                requires_confirmation=False,
            )

        # La herramienta necesita confirmación y aún no fue confirmada
        if not confirmed:
            message = "Esta acción requiere confirmación del usuario."

            if tool_name:
                message = (
                    f"La herramienta '{tool_name}' requiere "
                    "confirmación antes de ejecutarse."
                )

            return ConfirmationResult(
                allowed=False,
                requires_confirmation=True,
                message=message,
            )

        # El usuario ya confirmó la acción
        return ConfirmationResult(
            allowed=True,
            requires_confirmation=True,
            message="Acción confirmada por el usuario.",
        )