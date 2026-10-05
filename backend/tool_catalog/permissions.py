"""Comprobación de permisos del catálogo."""


def is_allowed(tool, granted_permissions):
    """Indica si los permisos otorgados cubren los requeridos por la tool."""
    granted = set(granted_permissions or [])
    required = set(tool.get("permissions", []))
    return required.issubset(granted)
