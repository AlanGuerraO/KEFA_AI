# KEFA AI — Frontend

Proyecto Vite + React (JavaScript). Implementa el diseño ya definido:
acento índigo + Space Grotesk/IBM Plex Sans en modo claro, paleta de
identidad de marca en modo oscuro (ver `src/styles/tokens.css`).

## Requisitos

- Node.js 18 o superior (recomendado 20 LTS).
- Backend corriendo en `http://localhost:8000` (o la URL que definas en `.env`).

## Puesta en marcha

Este contenedor no tiene salida a internet, así que `npm install` debe
correrse en tu máquina, no aquí.

```bash
cd frontend
cp .env.example .env     # ajusta VITE_API_URL si tu backend no usa el puerto 8000
npm install
npm run dev
```

Abre `http://localhost:5173`. La pantalla de login redirige a `/dashboard`
(todavía sin autenticación real — ver los `TODO(backend)` en
`src/App.jsx` y `src/pages/Login.jsx`).

El punto (verde/rojo) junto al botón de tema en el dashboard confirma si
`GET /api/health/` responde — así validamos la integración CORS end-to-end
sin construir nada extra.

## Scripts

- `npm run dev` — servidor de desarrollo (puerto 5173).
- `npm run build` — build de producción en `dist/`.
- `npm run preview` — sirve el build de `dist/` localmente.

## Estructura

```text
src/
├── components/   Sidebar, Topbar, Logo, ThemeToggle, StatusDot
├── context/       ThemeContext (claro/oscuro, persistido en localStorage)
├── pages/         Login, Dashboard, Placeholder (rutas aún no construidas)
├── services/      api.js — cliente fetch hacia el backend
└── styles/        tokens.css (colores/tipografía) + global.css
```

## Decisiones tomadas en esta sesión

- **JavaScript**, no TypeScript — se puede migrar después si el equipo lo
  prefiere; no hay nada que lo impida estructuralmente.
- **react-router-dom** para las rutas.
- **fetch nativo** como cliente HTTP (sin axios) — son pocos endpoints por
  ahora; si crece la complejidad (interceptores, refresh de token), vale la
  pena reconsiderar.
- Sin Tailwind ni librería de componentes: CSS plano con variables, para no
  pelear contra un sistema de diseño ajeno al que ya aprobamos.

## Lo que falta (fuera de alcance de esta entrega)

- Autenticación real (depende de que el backend exponga JWT).
- Conversaciones, Configuración, Mi cuenta — hoy son placeholders.
- Confirmación de acciones sensibles (Biblia, sección 12) — se añade
  cuando exista el flujo de Tool Calling en el backend.
- Docker — lo integra el equipo de DevOps una vez que `package.json` y
  esta estructura estén validados.
