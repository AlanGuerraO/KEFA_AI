# Orquestador — KEFA AI

**Ticket:** KEFA-014 "Diseñar orquestador" → Jira KEFA-113 · **Responsable:** Fanny
**Ubicación:** `backend/orchestrator/`
**Última actualización:** 11 de octubre de 2026 (código: `develop` @ `954b34b`)

> **Estado real:** son los componentes base, probados de forma aislada. **Todavía no están conectados** a la API, al catálogo de herramientas, al LLM ni a la base de datos. Ningún endpoint ni módulo del backend los importa.

---

## 1. Objetivo y responsabilidad

Decidir qué hacer con una acción que el LLM propone, siguiendo el principio de la Biblia: **la IA propone → el sistema valida → el sistema ejecuta**.

Para cada solicitud, el orquestador debe responder una de tres cosas: `execute`, `request_confirmation` o `reject`. No ejecuta herramientas ni llama a n8n.

---

## 2. Componentes

| Módulo | Clase principal | Responsabilidad |
|---|---|---|
| `input.py` | `OrchestratorInput` | Entrada: `user_id`, `message`, `session_id` (opcional) y `context`. `validate()` exige `user_id` y `message` no vacíos y `context` como diccionario. |
| `output.py` | `OrchestratorOutput` | Salida estándar: `success`, `message`, `action`, `tool`, `data`, `error`, `requires_confirmation`. Constructores `successful()` y `failed()`, y `to_dict()`. |
| `tool_validation.py` | `ToolValidator` | Comprueba que la herramienta exista en el catálogo recibido, que su `status` sea `cataloged` o `active` y que tenga `parameters`. |
| `parameter_validation.py` | `ParameterValidator` | Valida los parámetros contra el esquema: obligatorios presentes, ningún parámetro fuera del esquema y tipos correctos (rechaza `bool` como `integer`/`number`). |
| `permission_control.py` | `PermissionController` | Compara los permisos del usuario con los requeridos por la herramienta e indica el primero que falta. |
| `confirmation.py` | `ConfirmationManager` | Indica si una herramienta exige confirmación y si ya fue confirmada. |
| `decision_flow.py` | `DecisionFlow`, `DecisionType` | Combina los resultados anteriores y decide. |
| `error_handler.py` | `ErrorHandler` | Errores controlados con códigos fijos; `from_exception` expone solo el nombre del tipo de excepción. |
| `action_log.py` | `ActionLogger` | Registro de acciones **en memoria** (`log`, `get_records`, `clear`). |
| `tests.py` | `TestOrchestrator` | 8 pruebas unitarias. |

---

## 3. Flujo de decisión

`DecisionFlow.decide(...)` evalúa en este orden y se detiene en la primera condición que falla:

| Orden | Condición | Resultado | Motivo devuelto |
|---|---|---|---|
| 1 | No hay `tool_name` o la herramienta no existe | `reject` | La herramienta solicitada no existe. |
| 2 | Los parámetros no son válidos | `reject` | Los parámetros de la herramienta no son válidos. |
| 3 | El usuario no tiene permisos | `reject` | El usuario no tiene permisos para ejecutar esta herramienta. |
| 4 | Requiere confirmación y no está confirmada | `request_confirmation` | La acción requiere confirmación del usuario. |
| 5 | Todo correcto | `execute` | La herramienta puede ejecutarse. |

La decisión se devuelve como `OrchestratorDecision(decision, tool_name, reason)`.

```text
Mensaje → [LLM propone tool + parámetros] → ToolValidator → ParameterValidator
        → PermissionController → ¿requiere confirmación? → decide() → execute / request_confirmation / reject
```

Los pasos entre corchetes **no existen todavía**; el resto está implementado como componentes independientes.

---

## 4. Códigos de error

| Código | Mensaje |
|---|---|
| `INVALID_INPUT` | La entrada recibida no es válida. |
| `TOOL_NOT_FOUND` | La herramienta solicitada no existe. |
| `INVALID_PARAMETERS` | Los parámetros de la herramienta no son válidos. |
| `PERMISSION_DENIED` | El usuario no tiene permisos suficientes. |
| `CONFIRMATION_REQUIRED` | La acción requiere confirmación del usuario. |
| `EXECUTION_ERROR` | Ocurrió un error al ejecutar la herramienta. |
| `INTERNAL_ERROR` | Ocurrió un error interno en el orquestador. |

---

## 5. Relación con `tool_catalog`

Ambos paquetes cubren pasos parecidos, y hoy no encajan directamente:

| Tema | `tool_catalog` | `orchestrator` |
|---|---|---|
| Estructura del catálogo | `TOOL_CATALOG` es una **lista** (`get_tool`, `list_tools`) | `ToolValidator.validate` espera un **diccionario** por nombre |
| Validación de parámetros | `validate_tool_call` | `ParameterValidator` |
| Permisos | `is_allowed` | `PermissionController` |
| Confirmación | Marca `requires_confirmation` por herramienta; `ConfirmationRequiredError` | `ConfirmationManager` y `DecisionFlow` |

**Decisión pendiente (Fanny):** definir una única fuente de verdad para estas validaciones y el adaptador entre ambos (Jira KEFA-136 a 138).

---

## 6. Seguridad

- **Confirmación.** `decide()` recibe `confirmed` como argumento. Ese valor debe venir de una confirmación del usuario guardada en el servidor, nunca de la salida del LLM ni de los parámetros de la herramienta; de lo contrario el modelo podría saltarse la confirmación.
- **Parámetros desconocidos.** Se rechazan, lo que limita la manipulación de parámetros.
- **Permisos.** Los permisos del usuario deben calcularse en el backend a partir de la sesión autenticada.
- **Errores.** `from_exception` no expone el mensaje de la excepción, solo su tipo.
- **Registro.** El docstring de `ActionLogger` indica no guardar contraseñas, tokens ni credenciales, pero el código no lo impone: quien llame debe filtrar los `details`.

---

## 7. Limitaciones conocidas (verificadas en el código)

- No hay `__init__.py`: el descubrimiento automático de `manage.py test` probablemente no encuentra sus pruebas.
- `ActionLogger` guarda en memoria: el historial se pierde al reiniciar y no hay modelo de base de datos para acciones (Jira KEFA-122).
- `ParameterValidator` solo comprueba obligatorios, parámetros permitidos y tipo; no valida longitudes, formatos ni valores permitidos del esquema. Un tipo desconocido se acepta sin comprobar.
- No se llama al LLM ni a n8n.
- No hay endpoint que reciba un `OrchestratorInput`.

---

## 8. Pruebas

8 pruebas en `tests.py`, ejecutadas el 11-oct-2026: **8/8 OK**.

`test_input`, `test_output_success`, `test_parameter_validation`, `test_permission_control`, `test_confirmation_required`, `test_decision_flow_execute`, `test_error_handler`, `test_action_log`.

Cómo ejecutarlas (no necesitan Django ni base de datos), desde `backend/`:

```bash
python -m unittest orchestrator.tests -v
```

**Cobertura (verificada leyendo `tests.py`):** las pruebas cubren sobre todo el camino feliz. Un parámetro válido, un permiso concedido y una decisión `execute`; solo hay un caso negativo (confirmación requerida y no otorgada).

**Casos sin cubrir:**

- Parámetros inválidos, faltantes o con tipo incorrecto en `ParameterValidator`.
- Permiso faltante en `PermissionController`.
- Decisiones `reject` y `request_confirmation` en `DecisionFlow`, y el caso `confirmed=True`.
- `ToolValidator` completo (herramienta inexistente, estado no disponible, sin `parameters`).
- `ErrorHandler.from_exception` y `OrchestratorInput.validate` con entradas inválidas.
- `OrchestratorOutput.failed`.

---

## 9. Pendientes

| Pendiente | Ticket Jira |
|---|---|
| Añadir `__init__.py` y completar las pruebas de casos negativos (sección 8) | Por crear |
| Adaptador con `tool_catalog` y fuente única de validación | KEFA-136, 137, 138 |
| Persistir el registro de acciones | KEFA-122 |
| Flujo de confirmación con el usuario (solicitud, espera, registro) | KEFA-144 a 152 |
| Conexión con el LLM | KEFA-126, 127 |
| Endpoint que reciba mensajes y use el orquestador | Por crear |
