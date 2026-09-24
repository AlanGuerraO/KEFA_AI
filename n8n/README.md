# n8n — Workflows de KEFA AI

Esta carpeta contiene los workflows de n8n exportados como JSON, según la estructura definida en la Biblia del Proyecto (sección 15).

## Regla operativa: sanitización antes de comitear

Los exports de n8n (`n8n/workflows/*.json`) **sí se versionan en Git**, a diferencia de `.env` o credenciales sueltas. Sin embargo, un export de n8n puede incluir credenciales embebidas en el JSON (tokens de OAuth, API keys de servicios conectados, etc.) si no se sanitizan antes de exportar.

**Antes de comitear cualquier workflow nuevo o modificado:**

1. Exportar el workflow desde n8n.
2. Abrir el JSON y verificar manualmente que no existan valores de credenciales embebidos (buscar campos como `apiKey`, `token`, `accessToken`, `password`, `clientSecret`, etc. con valores reales en lugar de referencias).
3. Si n8n embebió una credencial real, reemplazarla por una referencia a la credencial gestionada dentro de n8n (credential reference), no por el valor en texto plano.
4. Solo después de confirmar que el JSON está limpio, agregarlo al commit.

Este paso es parte del checklist obligatorio en `.github/PULL_REQUEST_TEMPLATE.md` para cualquier PR que modifique `n8n/workflows/`.

## Responsable

Según la Biblia del Proyecto (sección 9), la automatización e integraciones (n8n, webhooks) es responsabilidad principal del Integrante 3 (Eric), pero la verificación de sanitización aplica a cualquier persona que exporte o modifique un workflow.
