class ToolCatalogError(Exception):
    """Error base del catálogo de herramientas."""


class UnknownToolError(ToolCatalogError):
    """La herramienta solicitada no existe en el catálogo."""


class ValidationError(ToolCatalogError):
    """Los parámetros no cumplen el schema definido para la herramienta."""


class PermissionDeniedError(ToolCatalogError):
    """El usuario no tiene el permiso requerido."""


class ConfirmationRequiredError(ToolCatalogError):
    """La acción es sensible y requiere confirmación explícita."""


class ToolExecutionError(ToolCatalogError):
    """La ejecución de una herramienta falló."""
