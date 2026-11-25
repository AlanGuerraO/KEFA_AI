# Frontend KEFA — Actualización sobre versión 4

## Alcance

- Se corrigió la desconexión de los modos de ejecución React → Django (`ejecutar` booleano).
- La pantalla Conversaciones tiene dos modos separados: Analizar (sin efectos externos) y Ejecutar en n8n (solo tras aceptar una advertencia).
- Se añadió bloqueo inmediato contra múltiples clics mientras una solicitud está en curso; **no sustituye la idempotencia de backend**.
- Los errores HTTP 409 conservan las decisiones de herramientas devueltas en el cuerpo de respuesta.
- Las respuestas de red inciertas tras ejecución no se interpretan como fallos seguros ni como éxitos.
- Las confirmaciones positivas se inhabilitaron temporalmente porque el endpoint existente devuelve HTTP 501. Cancelar sigue usando el endpoint real.
- El estado `accepted` de n8n aparece como pendiente, nunca como tarea creada; `verified` requiere estado de éxito con ID externo.
- La pantalla, actividad y dashboard distinguen los estados anteriores.
- Se retiró `Placeholder.jsx` sin uso, se fijó `npm ci` para reproducibilidad de Docker, se agregó `KEFA_N8N_EXECUTION_ENABLED=false` en la plantilla de configuración.

## Pruebas realizadas

- `npm test`: 20/20 pruebas correctas, incluyendo envío con y sin ejecución, errores HTTP y estados inciertos.
- 25 archivos JS/JSX: análisis sintáctico con @babel/parser sin errores.
- No fue posible instalar las dependencias con `npm ci --offline` por ausencia de caché de npm en este entorno. `npm run build` y la prueba en navegador con backend real siguen por ejecutar en tu PC.

## Límite fuera del frontend

El backend de la versión 4 todavía no devuelve el identificador real de Google tras `accepted`, no admite confirmación positiva (HTTP 501), no ofrece auditoría persistente ni protección permanente contra duplicados. La variable `KEFA_N8N_EXECUTION_ENABLED=true`, el webhook real, las credenciales y el permiso del usuario son requisitos para intentar ejecutar. La interfaz no puede resolver estos límites por sí sola.

## Comprobación local

1. Configurar `.env` en raíz y `frontend/.env` localmente, conservar los secretos de Docker; **nunca incluir en Git ni en ZIP**.
2. `cd frontend && npm ci && npm test && npm run build`.
3. Desde la raíz: `docker compose up -d --build` y `docker compose run --rm backend python manage.py migrate`.
4. Probar **Analizar** primero: ver `prepared`.
5. Preparar cuenta de prueba (permiso `users.kefa_tasks_write`) y el workflow n8n, habilitar ejecución en `.env`, reconstruir backend y elegir **Ejecutar**. `accepted` no es prueba de éxito; confirmar la tarea en Google Tasks antes de repetir.

Responsabilidad frontend: ticket KEFA-192, PR a la rama protegida `develop` tras pruebas locales y revisión humana.
