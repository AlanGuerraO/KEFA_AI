
"""KEFA-017: preparación segura de acciones confirmadas."""

from tool_catalog.registry import prepare_tool_call
from orchestrator.confirmation_store import confirmation_store


class InvalidConfirmationError(Exception):
    """La confirmación no es válida o ya fue consumida."""


def prepare_confirmed_action(
    request_id: str,
    user_id: str,
    granted_permissions=None,
):
    """
    Valida y consume una confirmación pendiente.

    No ejecuta herramientas externas.
    """

    if not isinstance(request_id, str) or not request_id.strip():
        raise InvalidConfirmationError(
            "El identificador de confirmación es obligatorio."
        )

    if not isinstance(user_id, str) or not user_id.strip():
        raise InvalidConfirmationError(
            "El identificador del usuario es obligatorio."
        )

    # Los permisos deben proceder del servidor.
    if not isinstance(granted_permissions, (list, tuple, set)):
        raise InvalidConfirmationError(
            "Se requieren permisos validados por el servidor."
        )

    solicitud = confirmation_store.get(request_id)

    if solicitud is None:
        raise InvalidConfirmationError(
            "Solicitud inexistente o vencida."
        )

    # Validar herramienta, parámetros y permisos antes de consumir.
    payload = prepare_tool_call(
        solicitud.tool_name,
        solicitud.parameters,
        granted_permissions=granted_permissions,
        confirmed=True,
    )

    # El consumo verifica atómicamente usuario, vigencia,
    # herramienta, parámetros y uso único.
    consumida = confirmation_store.consume(
        request_id,
        user_id,
        tool_name=solicitud.tool_name,
        parameters=solicitud.parameters,
    )

    if consumida is None:
        raise InvalidConfirmationError(
            "Confirmación no autorizada, vencida o ya utilizada."
        )

    return payload
