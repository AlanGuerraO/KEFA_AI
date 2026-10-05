# Tool Catalog — KEFA AI

Este paquete contiene el catálogo autorizado de herramientas del orquestador.

La IA solo puede **proponer** una herramienta. `validate_tool_call()` comprueba
que exista, que sus parámetros sean válidos, que el usuario tenga permisos y,
cuando corresponda, que exista confirmación explícita antes de preparar la
acción para n8n.

La documentación funcional está en `docs/tools/catalogo-herramientas.md`.
