
"""KEFA-016: integración segura de Tool Calling con Claude."""

import os
from copy import deepcopy

from config.claude_client import get_claude_client
from tool_catalog.catalog import list_tools
from tool_catalog.registry import prepare_tool_call
from tool_catalog.errors import ToolCatalogError


def build_claude_tools():
    """Convierte el catálogo autorizado al formato de Anthropic."""
    definitions = []
    name_map = {}

    for tool in list_tools():
        # Evitamos caracteres especiales en los nombres de la API.
        api_name = tool["name"].replace(".", "__")

        if api_name in name_map:
            raise ValueError("Nombre de herramienta duplicado.")

        name_map[api_name] = tool["name"]

        schema = deepcopy(tool["parameters"])
        for prop in schema.get("properties", {}).values():
            if prop.get("type") == "date-time":
                prop["type"] = "string"
                prop["format"] = "date-time"

        definitions.append({
            "name": api_name,
            "description": tool["description"],
            "input_schema": schema,
        })

    return definitions, name_map


class ToolCallingService:
    """Solicita herramientas a Claude sin ejecutarlas directamente."""

    def __init__(self, client=None, model=None):
        self.client = client
        self.model = model or os.getenv(
            "ANTHROPIC_MODEL", "claude-sonnet-4-5"
        )

    def procesar(self, mensaje, granted_permissions=None,
                 confirmed=False):
        if not isinstance(mensaje, str) or not mensaje.strip():
            raise ValueError("El mensaje no puede estar vacío.")

        definitions, name_map = build_claude_tools()

        if self.client is None:
            self.client = get_claude_client()
        try:
            respuesta = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=(
                    "Eres KEFA IA. Usa únicamente las herramientas "
                    "disponibles cuando sea necesario. No afirmes "
                    "que una acción se ejecutó si solo fue preparada."
                ),
                messages=[
                    {"role": "user", "content": mensaje}
                ],
                tools=definitions,
                tool_choice={"type": "auto"},
            )
        except (ConnectionError, TimeoutError):
            return [{
                "type": "error",
                "code": "claude_api_error",
                "message": "No se pudo comunicar con Claude.",
            }]

        resultados = []

        for bloque in respuesta.content:
            if bloque.type == "text":
                resultados.append({
                    "type": "text",
                    "text": bloque.text,
                })
                continue

            if bloque.type != "tool_use":
                continue

            nombre_real = name_map.get(bloque.name)

            if nombre_real is None:
                resultados.append({
                    "type": "error",
                    "code": "unknown_tool",
                    "message": "Herramienta no autorizada.",
                })
                continue

            try:
                payload = prepare_tool_call(
                    nombre_real,
                    bloque.input,
                    granted_permissions=granted_permissions,
                    confirmed=confirmed,
                )
                resultados.append({
                    "type": "tool_call",
                    "tool_use_id": bloque.id,
                    "status": "prepared",
                    "payload": payload,
                })
            except ToolCatalogError as error:
                resultados.append({
                    "type": "error",
                    "tool": nombre_real,
                    "code": type(error).__name__,
                    "message": str(error),
                })

        return resultados
