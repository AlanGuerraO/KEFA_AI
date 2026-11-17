# KEFA AI — Frontend conectado al orquestador (KEFA-192)

React 18 + Vite 5, JavaScript/JSX y CSS adaptable, con estilos claro y oscuro.

## Qué está implementado

| Pantalla | Funciones |
|---|---|
| `/login` y `/registro` | Autenticación con API Django, JWT y manejo de errores |
| `/dashboard` | Resumen de las solicitudes de la sesión y accesos directos reales |
| `/conversaciones` | Envío real a `POST /api/ai/tool-calling/`; resultados de herramientas, errores, estados, solicitud de confirmación/cancelación, ejemplos y diseño tipo chat |
| `/actividad` | Consulta, filtros, búsqueda, exportación JSON y eliminación del historial **local de esta pestaña** |
| `/integraciones` | Servicios, requisitos de conexión y estado **no verificado**, sin controles OAuth falsos |
| `/configuracion` | Tema claro/oscuro, prueba real de `/api/health/` y borrado de historial |
| `/cuenta` | Datos del usuario y recarga autenticada desde `/api/users/me/` |

El frontend renueva el JWT cuando el servidor devuelve 401 (si existe un refresh token válido), no envía contraseñas de Google o n8n y muestra estados de carga, error, confirmación y resultados. El historial visual usa `sessionStorage`, está separado por usuario y se borra al cerrar sesión.

## IMPORTANTE: límites del backend actual

El frontend está preparado y **hace peticiones reales**, pero la versión 3 del backend **todavía no ejecuta las herramientas en n8n**. `POST /api/ai/tool-calling/` devuelve, por ejemplo, `status: "prepared"`, que **NO** significa tarea creada. Los botones de confirmación llaman a la API real, pero confirmar devuelve `HTTP 501` en esta versión; cancelar sí puede responder `cancelled`.

Tampoco existe una API de historial persistente ni de estado OAuth por usuario. Actividad es un registro **local** en la pestaña; Integraciones muestra pasos de configuración, no conexiones verificadas.

### Contrato del frontend

```http
POST /api/ai/tool-calling/
Authorization: Bearer <JWT>
Content-Type: application/json

{"mensaje": "Crea una tarea llamada Prueba del proyecto"}
```

Respuesta del backend de la versión 3:

```json
{
  "resultados": [
    {
      "decision": "execute",
      "tool": "tasks.create",
      "reason": "Herramienta validada y preparada.",
      "status": "prepared",
      "request_id": null
    }
  ]
}
```

Para responder a una solicitud pendiente:

```http
POST /api/ai/confirmar-accion/
Authorization: Bearer <JWT>
Content-Type: application/json

{"request_id": "ID_DEVUELTO_POR_BACKEND", "respuesta": "cancelar"}
```

Valores aceptados: `confirmar`, `rechazar`, `cancelar`. La autorización real debe seguir validándose en Django, no desde React.

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

Desde el proyecto completo con Docker configurado: `docker compose up -d --build`, `docker compose run --rm backend python manage.py migrate`. Si no existen los archivos de secretos, créalos a partir de las plantillas; nunca publiques contraseñas.

## Pruebas

`npm test` ejecuta pruebas unitarias de cliente HTTP y normalización de respuestas (incluida la distinción entre preparado y ejecutado). No reemplazan una prueba real con Django, Claude y n8n.

## Responsabilidades de la siguiente fase

- Kevin/Fanny: ejecutar únicamente herramientas autorizadas y devolver su resultado verificable. Terminar confirmaciones positivas, permisos por usuario y auditoría persistente.
- Eric: verificar webhook de n8n, credenciales autorizadas y respuesta de Google Tasks/Calendar.
- Alan: validar visualmente en Docker, corregir cualquier diferencia de contrato y realizar el PR de KEFA-192 hacia `develop`.

**Seguridad:** La sesión usa `sessionStorage` para JWT. Revisar CSP/XSS, expiraciones, errores de API y CSRF/CORS según el método de autenticación antes de desplegar fuera del laboratorio.
