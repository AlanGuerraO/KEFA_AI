"""KEFA-183: envío explícito y controlado de una propuesta a n8n.

No acepta permisos del cliente ni afirmaciones de confirmación. Revalida contra
el catálogo justo antes del envío. No ejecuta acciones confirmables (KEFA-017).
"""

import os

from tool_catalog.catalog import get_tool
from tool_catalog.errors import ToolCatalogError
from tool_catalog.n8n_client import execute_n8n_tool
from tool_catalog.registry import prepare_tool_call


class DispatchDisabledError(Exception):
    """La integración está desactivada deliberadamente."""


class DispatchRejectedError(Exception):
    """La propuesta no es apta para envío automático."""


def is_dispatch_enabled():
    return os.getenv("KEFA_N8N_EXECUTION_ENABLED", "false").strip().lower() == "true"


def dispatch_prepared_call(prepared_call, *, granted_permissions=None):
    """Envía una sola acción validada; nunca considera aceptada = completada.

    Solo el servidor debe suministrar granted_permissions. No recibe confirmed,
    request_id ni otros datos de autorización desde el cliente.
    """
    if not is_dispatch_enabled():
        raise DispatchDisabledError("La ejecución con n8n está deshabilitada.")

    if not isinstance(prepared_call, dict):
        raise DispatchRejectedError("Solicitud preparada inválida.")
    name = prepared_call.get("tool")
    parameters = prepared_call.get("parameters")
    tool = get_tool(name) if isinstance(name, str) else None
    if tool is None:
        raise DispatchRejectedError("Herramienta desconocida.")

    # La confirmación se gestiona en otra ruta; no aceptar confirmed=True aquí.
    if tool.get("risk", {}).get("requires_confirmation"):
        raise DispatchRejectedError("Acción sensible: requiere flujo confirmado independiente.")

    # No confiamos en `execution` ni en cualquier otra propiedad del payload.
    try:
        validated = prepare_tool_call(
            name,
            parameters,
            granted_permissions=granted_permissions,
            confirmed=False,
        )
    except ToolCatalogError as exc:
        raise DispatchRejectedError("La propuesta no superó la validación del catálogo.") from exc

    if validated.get("execution", {}).get("method") != "n8n":
        raise DispatchRejectedError("Método de ejecución no admitido.")

    response = execute_n8n_tool(validated)
    if not isinstance(response, dict) or response.get("status") != "accepted":
        raise DispatchRejectedError("n8n no confirmó la recepción de la solicitud.")

    return {"status": "accepted", "http_status": response.get("http_status")}
