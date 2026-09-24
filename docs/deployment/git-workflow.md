# Flujo de Git y GitHub — KEFA AI

Este documento formaliza las decisiones de equipo tomadas en el **Chat 08 (DevOps e Infraestructura)**, con base en la Biblia del Proyecto (secciones 15, 17 y 18).

---

## 1. Estrategia de ramas

```text
main        → versión estable/desplegable
develop     → integración de features antes de pasar a main
feature/KEFA-XXX-descripcion
bugfix/KEFA-XXX-descripcion
```

Reglas:

- Toda rama `feature/*` o `bugfix/*` debe corresponder a una tarea real registrada en Jira/Trello (`KEFA-XXX`).
- No se crean ramas por integrante ni por preguntas o consultas de contexto técnico.
- `feature/*` y `bugfix/*` se integran primero a `develop`, nunca directo a `main`.
- `main` y `develop` están protegidas (ver sección 5).

---

## 2. Convención de commits

Formato basado en **Conventional Commits**, con scope obligatorio referenciando el ticket:

```text
tipo(KEFA-XXX): descripción breve en presente
```

Ejemplo:

```text
feat(KEFA-032): implement tool calling
security(KEFA-045): sanitize webhook payload from n8n
```

### Tipos permitidos

| Tipo | Uso |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `docs` | Documentación |
| `test` | Pruebas |
| `refactor` | Refactorización sin cambio de comportamiento |
| `chore` | Mantenimiento, configuración, dependencias |
| `security` | Cambios relacionados con seguridad (decisión de equipo) |
| `style` | Formato, sin cambios de lógica |
| `perf` | Mejoras de rendimiento |
| `build` | Build system |
| `ci` | Configuración de CI/CD |
| `revert` | Revertir un commit anterior |

El scope (`KEFA-XXX`) es **obligatorio**: no se aceptan commits sin referencia a un ticket.

---

## 3. Linter de commits (commitlint + husky)

Para que la convención anterior se cumpla automáticamente, el repositorio incluye:

- `package.json` (raíz) — dependencias de desarrollo (`husky`, `@commitlint/cli`, `@commitlint/config-conventional`).
- `commitlint.config.js` — reglas, incluyendo el tipo `security`.
- `.husky/commit-msg` — hook que valida el mensaje antes de aceptar el commit.

### Instalación (una sola vez por integrante, tras clonar el repo)

```bash
npm install
```

Esto ejecuta automáticamente el script `prepare` (`husky install`), que activa los hooks de Git.

> **Nota:** el archivo `.husky/commit-msg` debe tener permisos de ejecución. Si al clonar el repo el hook no se ejecuta, correr una vez:
> ```bash
> chmod +x .husky/commit-msg
> ```

### Comportamiento esperado

Un commit que no siga la convención será **rechazado** automáticamente:

```bash
$ git commit -m "arreglé un bug"
⧗   input: arreglé un bug
✖   subject may not be empty [subject-empty]
✖   type may not be empty [type-empty]
✖   found 2 problems
```

Un commit correcto:

```bash
$ git commit -m "fix(KEFA-051): correct timezone handling in calendar events"
✔ ok
```

---

## 4. Pull Requests

- Todo PR debe usar la plantilla en `.github/PULL_REQUEST_TEMPLATE.md`.
- Todo PR debe referenciar un ticket `KEFA-XXX`.
- **Se requiere 1 aprobación humana** antes de poder fusionar a `develop` (ver sección 5, configuración de branch protection).
- No se permite merge de `feature/*`/`bugfix/*` directo a `main`; siempre pasa por `develop` primero.
- Estrategia de merge, exigencia de CI en verde y número de aprobaciones para `main` quedan como configuración adicional a definir cuando exista pipeline de pruebas (no bloquea el MVP).

---

## 5. Protección de ramas

- `main`: ya protegida (configurada previamente por el equipo).
- `develop`: protegida con la misma lógica que `main`, agregando como mínimo:
  - Requerir Pull Request antes de fusionar.
  - Requerir **1 aprobación** antes de merge.
  - No permitir push directo a `develop`.

Los pasos exactos de configuración en GitHub se documentan de forma operativa en el Chat 08 (DevOps) y pueden repetirse aquí si el equipo lo solicita.

---

## 6. Qué se versiona y qué no

**Dentro de Git:** código fuente, `.env.example`, `docker-compose.yml` (sin secretos), documentación (`docs/`), tests, `package.json`/`commitlint.config.js`/`.husky/` (herramientas de commit), `.github/PULL_REQUEST_TEMPLATE.md`.

**Fuera de Git (`.gitignore`):** `.env` real, credenciales, `node_modules/`, entornos virtuales, volúmenes de PostgreSQL, `.vscode/` (ignorado por completo, decisión de equipo), archivos de sistema (`.DS_Store`, `Thumbs.db`).

---

## Estado

Estas reglas reflejan decisiones ya tomadas por el equipo. Cualquier cambio a esta estrategia debe documentarse como actualización de este archivo, y si modifica arquitectura o flujo del proyecto, considerar registrarlo como ADR en `docs/architecture/`.
