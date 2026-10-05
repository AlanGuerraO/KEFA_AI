# KEFA-013 — Catálogo de herramientas

## Objetivo

Definir una lista cerrada de herramientas que el orquestador de KEFA AI puede
proponer mediante Tool Calling. La IA **no ejecuta herramientas directamente**:
el backend valida la propuesta y solamente después prepara su ejecución por n8n.

## Regla de seguridad

> La IA propone una acción. El sistema decide si la acción está permitida. Después se ejecuta.

La fuente de verdad del catálogo está en `backend/tool_catalog/catalog.py`.

## 1. Schema de herramientas (KEFA-105)

Cada herramienta tiene esta estructura:

```text
name
 description
 category
 parameters
 permissions
 risk
 execution
```

`parameters` utiliza un subconjunto controlado de JSON Schema:

- `type`: object, string, boolean o date-time.
- `properties`: parámetros permitidos.
- `required`: parámetros obligatorios.
- `additionalProperties: false`: evita que la IA agregue parámetros no definidos.
- `minLength` y `maxLength`: límites para textos.

## 2. Descripción (KEFA-106)

| Herramienta | Descripción |
|---|---|
| `calendar.create_event` | Crea un evento en Google Calendar. |
| `calendar.get_events` | Consulta eventos dentro de un rango. |
| `calendar.update_event` | Actualiza un evento existente. |
| `calendar.delete_event` | Elimina un evento. |
| `tasks.create` | Crea una tarea en Google Tasks. |
| `tasks.list` | Consulta tareas. |
| `tasks.complete` | Marca una tarea como completada. |
| `tasks.delete` | Elimina una tarea. |
| `notion.create_page` | Crea una página en Notion. |
| `notion.search` | Busca páginas de Notion. |
| `notion.update_page` | Actualiza una página existente. |

## 3. Parámetros (KEFA-107)

### Google Calendar

- `calendar.create_event`: `title`, `start`, `end`, `description`.
- `calendar.get_events`: `start`, `end`.
- `calendar.update_event`: `event_id` y, opcionalmente, `title`, `start`, `end`, `description`.
- `calendar.delete_event`: `event_id`.

### Google Tasks

- `tasks.create`: `title`, `notes`, `due`.
- `tasks.list`: `completed` opcional.
- `tasks.complete`: `task_id`.
- `tasks.delete`: `task_id`.

### Notion

- `notion.create_page`: `title`, `content`, `parent_id`.
- `notion.search`: `query`.
- `notion.update_page`: `page_id`, `content` y `title` opcional.

## 4. Validaciones (KEFA-110)

Antes de preparar una ejecución, el backend verifica:

1. Que la herramienta exista en el catálogo.
2. Que los parámetros sean un objeto.
3. Que estén todos los parámetros requeridos.
4. Que no existan parámetros adicionales.
5. Que cada parámetro tenga el tipo esperado.
6. Que las cadenas respeten sus longitudes.
7. Que las fechas sean ISO 8601 válidas.
8. Que el usuario tenga los permisos requeridos.
9. Que una herramienta sensible tenga confirmación explícita.

## 5. Riesgos (KEFA-109)

| Nivel | Ejemplos | Control |
|---|---|---|
| Bajo | Consultar eventos, listar tareas, buscar Notion | Autenticación + permisos + schema |
| Medio | Crear/actualizar información | Autenticación + permisos + schema + auditoría |
| Alto | Eliminar eventos o tareas | Todos los controles anteriores + confirmación explícita |

La IA no puede crear una herramienta nueva ni ejecutar comandos fuera del
catálogo. Esto reduce el riesgo de Tool Manipulation y ejecución arbitraria.

## 6. Permisos (KEFA-108)

Se usan permisos de alcance reducido:

- `calendar:read`
- `calendar:write`
- `tasks:read`
- `tasks:write`
- `notion:read`
- `notion:write`

El backend debe comprobar estos permisos aunque el frontend o la IA indiquen
que una acción está permitida.

## 7. Manejo de errores (KEFA-111)

El catálogo define errores específicos para poder responder sin ejecutar una
acción insegura:

- `UnknownToolError`: herramienta inexistente.
- `ValidationError`: parámetros inválidos o incompletos.
- `PermissionDeniedError`: permisos insuficientes.
- `ConfirmationRequiredError`: acción sensible sin confirmación.
- `ToolExecutionError`: fallo al preparar la ejecución.

Los errores deben registrarse en el historial/auditoría sin guardar secretos,
tokens ni credenciales.

## 8. Ejecución

Por ahora el catálogo deja `execution.method = n8n` y `status = cataloged`. No
se implementa todavía la llamada real a n8n porque los workflows concretos y
las credenciales de las integraciones todavía están pendientes.

La integración futura deberá seguir este flujo:

```text
Usuario
  ↓
IA / Orquestador
  ↓ propone tool + parámetros
Catálogo
  ↓ valida
Permisos
  ↓ valida
Confirmación (si es sensible)
  ↓
n8n
  ↓
Servicio externo
  ↓
Resultado + auditoría
```

## Archivos relacionados

- `backend/tool_catalog/catalog.py` — catálogo y schema.
- `backend/tool_catalog/validation.py` — validaciones.
- `backend/tool_catalog/permissions.py` — permisos.
- `backend/tool_catalog/errors.py` — manejo de errores.
- `backend/tool_catalog/registry.py` — preparación de ejecución.
- `backend/tool_catalog/tests.py` — pruebas automatizadas.

## Estado de KEFA-013

| Subtarea | Resultado |
|---|---|
| KEFA-105 — Definir schema de herramientas | Implementado |
| KEFA-106 — Definir descripción | Implementado |
| KEFA-107 — Definir parámetros | Implementado |
| KEFA-110 — Definir validaciones | Implementado |
| KEFA-112 — Documentar catálogo | Implementado |
| KEFA-109 — Definir riesgos | Implementado |
| KEFA-108 — Definir permisos | Implementado |
| KEFA-111 — Definir manejo de errores | Implementado |
