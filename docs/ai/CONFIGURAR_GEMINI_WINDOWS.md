# Configurar Gemini en KEFA AI — Windows, PowerShell y Docker

Este proyecto usa **Gemini por defecto**, mediante la API REST oficial `generateContent`, sin instalar un SDK de Google adicional. Mantiene una alternativa `anthropic` para quien tenga créditos de Claude. **No necesitas una suscripción a Gemini Advanced ni pagar a Anthropic** para ejecutar Gemini con cuota gratuita, *siempre que Google ofrezca ese nivel para tu modelo, proyecto y región*.

## 1. Crear tu proyecto y clave en Google AI Studio

1. Abre [Google AI Studio — API Keys](https://aistudio.google.com/apikey) en tu navegador.
2. Inicia sesión con tu cuenta personal de Google y acepta los términos que te solicite. No es necesario crear una segunda cuenta de Gmail.
3. Haz clic en **Create API key** / **Crear clave de API**.
4. Selecciona el proyecto de Google Cloud sugerido o crea uno nuevo llamado, por ejemplo, `KEFA-AI-Desarrollo`.
5. Genera la clave y cópiala en un lugar privado. Para este proyecto **no publiques la clave ni la pegues en chats, capturas, GitHub o Jira**.
6. En el panel de **Usage / Rate limits** revisa si tu proyecto y el modelo seleccionado tienen cuota gratuita. Revisa la [tabla oficial de precios](https://ai.google.dev/gemini-api/docs/pricing) antes de vincular facturación.
7. Restringe la clave para que se utilice únicamente con la API de Gemini, cuando el panel permita configurarlo. La clave es solo para el **servidor Django**, nunca para React.

> Los límites gratuitos, modelos y condiciones de acceso pueden variar. El proyecto no crea una cuenta ni una clave automáticamente y no incluye claves reales.

## 2. Configurar tu archivo `.env` existente

En PowerShell, dentro de `D:\alang\Desktop\Proyecto_IA_KEFA`:

```powershell
# Si ya tienes .env NO lo sobreescribas: contiene tus otros secretos.
if (!(Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

Añade o modifica **solo estas variables**:

```dotenv
LLM_PROVIDER=gemini
GEMINI_API_KEY=PEGA_AQUI_TU_CLAVE_PRIVADA
GEMINI_MODEL=gemini-3.5-flash-lite
KEFA_TIMEZONE=America/Mexico_City
```

Puedes dejar `ANTHROPIC_API_KEY` vacío: el backend no llamará a Anthropic cuando `LLM_PROVIDER=gemini`.

**Nota**: `gemini-3.5-flash-lite` es el valor predeterminado configurable. Si Google indica que no está disponible para tu proyecto, elige un modelo estable disponible en AI Studio y actualiza `GEMINI_MODEL`.

## 3. Recrear el backend (para actualizar las variables)

Desde la carpeta raíz:

```powershell
docker compose config --quiet
docker compose up -d --build
docker compose run --rm backend python manage.py migrate
docker compose exec backend python scripts/verificar_gemini.py
```

Salida esperada:

```text
Proveedor: gemini
Modelo Gemini: gemini-3.5-flash-lite
GEMINI_API_KEY configurada: True
Configuración local lista.
```

La clave se mantiene privada: el script solo devuelve un booleano.

## 4. Primera prueba contra Google (sin n8n)

Esta llamada consume cuota real de la API:

```powershell
docker compose exec backend python scripts/verificar_gemini.py --live
```

Si responde, prueba el Tool Calling **sin ejecutar operaciones**:

```powershell
docker compose exec backend python -c "from services.tool_calling_service import ToolCallingService; print(ToolCallingService().procesar('¿Qué puedes hacer?'))"
```

Después abre http://localhost:5173, inicia sesión, entra a **Conversaciones**, selecciona **Solo analizar** y escribe `Crea una tarea llamada Prueba del proyecto`.

- Si aparece «Herramienta preparada», Gemini interpretó la solicitud pero **NO** creó la tarea.
- Si aparece «Sin permisos», verifica el permiso `users.kefa_tasks_write` en Django Admin para la cuenta de pruebas.
- Si responde con texto pidiendo una aclaración, ese texto llega ahora a Conversaciones.

## 5. Ejecutar una tarea real en Google Tasks (opcional)

No basta con la clave de Gemini. El equipo también debe tener preparado el webhook de n8n, sus credenciales y Google Tasks en una cuenta de prueba.

1. Comprueba que Eric logró crear tareas desde n8n y que el webhook productivo esté activo.
2. Comprueba que el usuario Django de prueba tenga el permiso `users.kefa_tasks_write` y que el backend cargue el secreto de Basic Auth de n8n.
3. Cambia `KEFA_N8N_EXECUTION_ENABLED=true` en `.env`.
4. Ejecuta `docker compose up -d --force-recreate backend`.
5. Selecciona **Ejecutar en n8n** desde Conversaciones; revisa cualquier advertencia y **haz una sola solicitud**.
6. Comprueba la tarea en Google Tasks. El backend todavía devuelve `accepted`, que **no significa creación confirmada**; evita reintentar si una llamada falla sin respuesta.

**Límites pendientes de otros módulos**: confirmaciones positivas aún devuelven HTTP 501, n8n no devuelve siempre el ID de Google, el historial es de sesión y falta idempotencia persistente. Esto no lo soluciona cambiar de proveedor IA.

## 6. Errores frecuentes

| Diagnóstico | Qué revisar |
|---|---|
| `GEMINI_API_KEY no está configurada` | Clave real en `.env` raíz y recrear backend |
| HTTP 400 | El modelo no acepta el esquema de función; revisar nombre del modelo y API |
| HTTP 401 o 403 | Clave incorrecta, permisos del proyecto, región o API restringida |
| HTTP 404 | Modelo no disponible; actualizar `GEMINI_MODEL` |
| HTTP 429 | Cuota gratuita agotada o límite temporal; revisar Usage / Rate limits |
| HTTP 502 en React | `docker compose logs -f --tail=100 backend` y ejecutar `verificar_gemini.py --live` |
| `n8n deshabilitado` | La variable `KEFA_N8N_EXECUTION_ENABLED` sigue en `false` |
| Rechazo `tasks:write` | El usuario Django no tiene permiso para crear tareas |

## 7. Comprobaciones y PR

```powershell
cd frontend
npm ci
npm test
npm run build
cd ..
docker compose run --rm backend python manage.py check
docker compose run --rm backend python manage.py test config users ai_api
```

Antes de subir cambios verifica que no estén rastreados `.env` ni `secrets/*.txt` reales:

```powershell
git status
git ls-files .env backend/.env frontend/.env secrets/
```

**Recomendado**: entregar los cambios en una rama `feature/` y abrir PR hacia `develop`, nunca actualizar directamente la rama protegida. Revisa los archivos backend junto con Fanny y Kevin por tratarse de módulos de IA y seguridad.
