# Frontend KEFA AI — experiencia de usuario final

**Actualización de noviembre de 2026:** La pantalla de Conversaciones presenta acciones y preguntas con lenguaje natural, confirma las solicitudes antes de enviarlas, y no equipara la recepción de n8n con una acción completada. El Resumen, Actividad, Integraciones, Configuración y Mi cuenta se ajustaron para el usuario final.

Para la guía paso a paso de demostración, pruebas e instalación, consulta `../GUIA_DEMOSTRACION_FRONTEND.md`.

---

# KEFA AI — Frontend versión 4 corregido (KEFA-192)

React 18 + Vite 5, JavaScript/JSX y CSS adaptable, con estilos claro y oscuro.

## Qué está implementado

| Pantalla | Funciones |
|---|---|
| `/login` y `/registro` | Autenticación con API Django, JWT y manejo de errores |
| `/dashboard` | Resumen de las solicitudes de la sesión y accesos directos reales |
| `/conversaciones` | Modo **Analizar** (`ejecutar:false`) o **Ejecutar en n8n** (`ejecutar:true`) con advertencia; decisiones de Claude, errores HTTP y estados inciertos, cancelación de confirmaciones, ejemplos y chat |
| `/actividad` | Consulta, filtros, búsqueda, exportación JSON y eliminación del historial **local de esta pestaña** |
| `/integraciones` | Servicios, requisitos de conexión y estado **no verificado**, sin controles OAuth falsos |
| `/configuracion` | Tema claro/oscuro, prueba real de `/api/health/` y borrado de historial |
| `/cuenta` | Datos del usuario y recarga autenticada desde `/api/users/me/` |

El frontend renueva el JWT cuando el servidor devuelve 401 (si existe un refresh token válido), no envía contraseñas de Google o n8n y muestra estados de carga, error, confirmación y resultados. El historial visual usa `sessionStorage`, está separado por usuario y se borra al cerrar sesión.

## IMPORTANTE: alcance exacto del backend de la versión 4

- `POST /api/ai/tool-calling/` recibe `{ "mensaje": "...", "ejecutar": false }` en **Analizar** y `{ "mensaje": "...", "ejecutar": true }` en **Ejecutar**. Este segundo modo puede despachar una acción real a n8n **solo si** `KEFA_N8N_EXECUTION_ENABLED=true`, se configuró el webhook/credenciales y el usuario tiene los permisos adecuados.
- La ejecución **requiere confirmación explícita del usuario desde la interfaz** antes de enviar la petición. La prevención de doble clic es local a la pestaña; el backend **todavía no implementa idempotencia persistente**, por lo que hay riesgo de duplicar acciones si se reenvía la instrucción tras un corte de red.
- En la versión 4, el backend devuelve `accepted` cuando n8n aceptó el HTTP. **Eso no prueba** que Google Tasks haya creado una tarea. Solo aparecerá un estado de resultado identificado si el backend llega a devolver `status: succeeded` junto con un `execution_result.id` (lo que todavía requiere desarrollo del backend).
- Si el envío se interrumpe mientras se solicita ejecutar, se marca como **resultado incierto**. Antes de repetir la petición, comprobar Google Tasks/Calendar.
- `POST /api/ai/confirmar-accion/` permite cancelar una solicitud, pero su rama positiva (`respuesta: confirmar`) aún devuelve **HTTP 501**. Por eso el botón de confirmación positiva está deshabilitado; no se simula éxito.
- El historial usa `sessionStorage` en la pestaña (no PostgreSQL). Integraciones tampoco tiene todavía API para verificar OAuth individual por usuario.

### Contrato HTTP

```http
POST /api/ai/tool-calling/
Authorization: Bearer <JWT>
Content-Type: application/json

{"mensaje":"Crea una tarea llamada Prueba del proyecto","ejecutar":false}
```

Para intentar el despacho real, el frontend envía el mismo JSON con `"ejecutar":true`, después de que el usuario lo autorice. Una respuesta típica **aún no verificada en Google** es:

```json
{
  "resultados": [
    {
      "decision": "execute",
      "tool": "tasks.create",
      "reason": "Herramienta validada",
      "status": "accepted",
      "http_status": 200,
      "request_id": null
    }
  ]
}
```

La respuesta anterior es ilustrativa del formato; no certifica que el flujo de Google haya terminado con éxito.

Para cancelar una confirmación pendiente:

```http
POST /api/ai/confirmar-accion/
Authorization: Bearer <JWT>
Content-Type: application/json

{"request_id":"ID_DEVUELTO_POR_BACKEND","respuesta":"cancelar"}
```

## Inicio rápido

1. Copia `frontend/.env.example` como `frontend/.env` (sin subir ese archivo a Git).
2. Verifica `VITE_API_URL=http://localhost:8080` si ese es el puerto publicado por Docker.
3. Ejecuta:

```bash
cd frontend
npm ci
npm test
npm run dev
```

Abre `http://localhost:5173`, registra o inicia sesión y entra a Conversaciones.

Para verificar compilación de producción en un equipo con dependencias disponibles:

```bash
npm run build
```

Desde el proyecto completo con Docker configurado: `docker compose up -d --build`, `docker compose run --rm backend python manage.py migrate`. Debes conservar los archivos de secretos de tu copia local (no están incluidos en los ZIP de entrega). En `.env`, agregar `KEFA_N8N_EXECUTION_ENABLED=true` **solo para probar en un entorno controlado**. Sin esa variable o sin permisos, el backend responde 503/403. Nunca publiques contraseñas.

## Pruebas

`npm test` ejecuta **20 pruebas** del cliente HTTP y la normalización, incluidos los dos modos, errores 409 y estados inciertos. Las 20 pasan en este entorno. El análisis sintáctico de 25 archivos JS/JSX no reportó errores. No se pudo ejecutar `npm run build` porque `npm ci --offline` carece de paquetes en caché; debes ejecutarlo en tu PC con acceso al registro de npm. Tampoco se realizaron pruebas reales con Django, Claude, n8n o Google.

## Responsabilidades de la siguiente fase

- Kevin/Fanny: ejecutar únicamente herramientas autorizadas y devolver su resultado verificable. Terminar confirmaciones positivas, permisos por usuario y auditoría persistente.
- Eric: verificar webhook de n8n, credenciales autorizadas y respuesta de Google Tasks/Calendar.
- Alan: validar visualmente en Docker, corregir cualquier diferencia de contrato y realizar el PR de KEFA-192 hacia `develop`.

**Seguridad:** La sesión usa `sessionStorage` para JWT. Revisar CSP/XSS, expiraciones, errores de API y CSRF/CORS según el método de autenticación antes de desplegar fuera del laboratorio.
