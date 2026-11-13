# KEFA AI — Frontend (revisión de la fase 2)

Interfaz **React 18 + Vite 5**, JavaScript/JSX y CSS modular sin librerías adicionales de componentes.

## Incluye

- Inicio de sesión con JWT, registro, renovación de token y perfil obtenido de Django.
- Layout profesional y adaptable: menú lateral, cabecera, tarjetas, tema claro/oscuro.
- **Resumen**: estado real de funcionalidades e introducción a tareas previstas (sin cifras inventadas).
- **Conversaciones**: preparación y copia local de instrucciones; el envío a la IA **aún no existe**.
- **Actividad**: pantalla para futuras auditorías; no presenta registros falsos.
- **Integraciones**: estado claramente pendiente de Telegram, Calendar, Tasks y Notion.
- **Configuración**: tema persistente y prueba real de `GET /api/health/`.
- **Mi cuenta**: perfil obtenido de `GET /api/users/me/` y actualización manual.
- Rutas de navegación protegidas; menú móvil y controles accesibles.

**No incluye todavía** ejecución de herramientas, OAuth de Google, historial persistido, notificaciones ni APIs del orquestador. El frontend las marca como pendientes y no simula resultados.

## Instalar y ejecutar

Se recomienda Node 22 o la versión compatible definida por el equipo.

```bash
cd frontend
cp .env.example .env
npm ci
npm run dev
```

Si usas Docker con el puerto del backend `8080`, la variable debe ser:

```dotenv
VITE_API_URL=http://localhost:8080
```

Para ejecutar todas las pruebas frontend disponibles y compilar:

```bash
npm test
npm run build
```

`npm test` utiliza el ejecutor de Node y prueba el cliente HTTP sin depender de un servidor ni de credenciales.

## Rutas

| Ruta | Pantalla | Estado |
|---|---|---|
| `/login` | Inicio de sesión | Conectada a API |
| `/registro` | Registro | Conectada a API |
| `/dashboard` | Resumen | Presentación real de estado |
| `/conversaciones` | Conversaciones | Redacción local; IA pendiente |
| `/actividad` | Actividad | UI lista; API pendiente |
| `/integraciones` | Integraciones | UI lista; OAuth pendiente |
| `/configuracion` | Configuración | Tema y healthcheck funcionales |
| `/cuenta` | Mi cuenta | Perfil real conectado |

## Seguridad

- No ingreses claves privadas ni tokens OAuth en el frontend.
- El login usa `sessionStorage` para JWT en esta versión. Debe mantenerse una **revisión de XSS/CSP y almacenamiento de sesión** antes de desplegar a internet.
- Confirmaciones de acciones sensibles deben validarse en backend, nunca solo en la interfaz.
- La protección del frontend no sustituye autorización y permisos por objeto en DRF.

Ver `docs/revisiones/revision-2026-11-10.md` para hallazgos y siguientes pasos.
