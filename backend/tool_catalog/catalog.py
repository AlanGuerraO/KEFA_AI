"""Catálogo autorizado de herramientas de KEFA AI.

La IA puede proponer una tool, pero nunca ejecutarla directamente. El backend
usa este catálogo como fuente de verdad para validar nombre, parámetros,
permisos, riesgo y confirmación antes de enviar la acción a n8n.
"""

from copy import deepcopy


def _tool(name, description, category, parameters, required_permissions,
          risk_level, requires_confirmation=False):
    return {
        "name": name,
        "description": description,
        "category": category,
        "parameters": {
            "type": "object",
            "properties": parameters,
            "required": required_permissions.get("required_parameters", []),
            "additionalProperties": False,
        },
        "permissions": required_permissions.get("permissions", []),
        "risk": {
            "level": risk_level,
            "requires_confirmation": requires_confirmation,
        },
        "execution": {
            "method": "n8n",
            "status": "cataloged",
        },
    }


TOOL_CATALOG = [
    _tool(
        "calendar.create_event",
        "Crea un evento en Google Calendar.",
        "calendar",
        {
            "title": {"type": "string", "minLength": 1, "maxLength": 200},
            "start": {"type": "date-time"},
            "end": {"type": "date-time"},
            "description": {"type": "string", "maxLength": 2000},
        },
        {"required_parameters": ["title", "start", "end"],
         "permissions": ["calendar:write"]},
        "medium",
    ),
    _tool(
        "calendar.get_events",
        "Consulta eventos de Google Calendar dentro de un rango de tiempo.",
        "calendar",
        {
            "start": {"type": "date-time"},
            "end": {"type": "date-time"},
        },
        {"required_parameters": ["start", "end"],
         "permissions": ["calendar:read"]},
        "low",
    ),
    _tool(
        "calendar.update_event",
        "Actualiza los datos de un evento existente.",
        "calendar",
        {
            "event_id": {"type": "string", "minLength": 1, "maxLength": 200},
            "title": {"type": "string", "minLength": 1, "maxLength": 200},
            "start": {"type": "date-time"},
            "end": {"type": "date-time"},
            "description": {"type": "string", "maxLength": 2000},
        },
        {"required_parameters": ["event_id"],
         "permissions": ["calendar:write"]},
        "medium",
    ),
    _tool(
        "calendar.delete_event",
        "Elimina un evento existente de Google Calendar.",
        "calendar",
        {
            "event_id": {"type": "string", "minLength": 1, "maxLength": 200},
        },
        {"required_parameters": ["event_id"],
         "permissions": ["calendar:write"]},
        "high",
        True,
    ),
    _tool(
        "tasks.create",
        "Crea una tarea en Google Tasks.",
        "tasks",
        {
            "title": {"type": "string", "minLength": 1, "maxLength": 500},
            "notes": {"type": "string", "maxLength": 5000},
            "due": {"type": "date-time"},
        },
        {"required_parameters": ["title"],
         "permissions": ["tasks:write"]},
        "medium",
    ),
    _tool(
        "tasks.list",
        "Consulta las tareas del usuario.",
        "tasks",
        {
            "completed": {"type": "boolean"},
        },
        {"required_parameters": [], "permissions": ["tasks:read"]},
        "low",
    ),
    _tool(
        "tasks.complete",
        "Marca una tarea de Google Tasks como completada.",
        "tasks",
        {
            "task_id": {"type": "string", "minLength": 1, "maxLength": 200},
        },
        {"required_parameters": ["task_id"],
         "permissions": ["tasks:write"]},
        "medium",
    ),
    _tool(
        "tasks.delete",
        "Elimina una tarea existente de Google Tasks.",
        "tasks",
        {
            "task_id": {"type": "string", "minLength": 1, "maxLength": 200},
        },
        {"required_parameters": ["task_id"],
         "permissions": ["tasks:write"]},
        "high",
        True,
    ),
    _tool(
        "notion.create_page",
        "Crea una página en Notion.",
        "notion",
        {
            "title": {"type": "string", "minLength": 1, "maxLength": 200},
            "content": {"type": "string", "minLength": 1, "maxLength": 10000},
            "parent_id": {"type": "string", "minLength": 1, "maxLength": 200},
        },
        {"required_parameters": ["title", "content", "parent_id"],
         "permissions": ["notion:write"]},
        "medium",
    ),
    _tool(
        "notion.search",
        "Busca páginas de Notion por texto.",
        "notion",
        {
            "query": {"type": "string", "minLength": 1, "maxLength": 500},
        },
        {"required_parameters": ["query"],
         "permissions": ["notion:read"]},
        "low",
    ),
    _tool(
        "notion.update_page",
        "Actualiza el contenido de una página existente de Notion.",
        "notion",
        {
            "page_id": {"type": "string", "minLength": 1, "maxLength": 200},
            "title": {"type": "string", "minLength": 1, "maxLength": 200},
            "content": {"type": "string", "minLength": 1, "maxLength": 10000},
        },
        {"required_parameters": ["page_id", "content"],
         "permissions": ["notion:write"]},
        "medium",
    ),
]


def get_tool(name):
    """Devuelve una copia de la definición de una tool para evitar mutaciones."""
    for tool in TOOL_CATALOG:
        if tool["name"] == name:
            return deepcopy(tool)
    return None


def list_tools(category=None):
    """Lista las herramientas autorizadas, opcionalmente por categoría."""
    tools = TOOL_CATALOG if category is None else [
        tool for tool in TOOL_CATALOG if tool["category"] == category
    ]
    return deepcopy(tools)
