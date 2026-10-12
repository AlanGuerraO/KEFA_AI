# Primeros pasos al clonar KEFA AI

Guía para cualquier integrante del equipo que clone el repositorio por primera vez. Sigue estos pasos en orden — evita los errores ya detectados durante el setup inicial (Chat 08).

**Última actualización:** 11 de octubre de 2026. Ubicación: `docs/deployment/primeros-pasos-clonar-repo.md`.

---

## 1. Requisitos previos

Antes de clonar, confirma que tienes instalado:

```bash
git --version
node --version
npm --version
```

**Windows:** instala "Git for Windows" (incluye **Git Bash**). Usa Git Bash para todos los comandos de este documento, **no PowerShell ni CMD** — varios comandos (`chmod`, por ejemplo) no existen ahí.

---

## 2. Clonar el repositorio

```bash
git clone git@github.com:AlanGuerraO/KEFA_AI.git
cd KEFA_AI
```

Verifica en qué rama quedaste por defecto:

```bash
git branch --show-current
```

Normalmente será `main`. Cambia a `develop`, que es donde vive el trabajo activo del equipo:

```bash
git checkout develop
git pull origin develop
```

> `main` queda reservada para versiones estables. Todo el desarrollo activo ocurre en `develop` y en ramas `feature/*`/`bugfix/*`.

---

## 3. Instalar dependencias y activar el linter de commits

```bash
npm install
```

Esto instala `husky`, `@commitlint/cli` y `@commitlint/config-conventional`, y ejecuta automáticamente el script `prepare` (`husky`), que configura los hooks de Git.

### Verificación obligatoria del hook (no te la saltes)

```bash
git config core.hooksPath
```

Debe apuntar a `.husky`. Si no aparece nada o da error, corre manualmente:

```bash
npm run prepare
```

### Permisos de ejecución del hook

Si estás en **Git Bash / Linux / macOS**:

```bash
chmod +x .husky/commit-msg
```

Si por alguna razón Git no reconoce el permiso al hacer `git status` (aparece como modificado sin que tú lo hayas tocado), fuerza el bit directamente en el índice:

```bash
git update-index --chmod=+x .husky/commit-msg
```

**Windows con `core.autocrlf=true`:** el repo ya incluye un `.gitattributes` que fuerza `LF` en `.husky/*` y `*.sh`, así que no deberías ver el warning de "LF will be replaced by CRLF" en este archivo. Si lo ves, confirma que tu copia local de `.gitattributes` esté actualizada (`git pull`) y vuelve a normalizar:

```bash
git add --renormalize .husky/commit-msg
```

---

## 4. Probar que el hook realmente funciona

```bash
# Debe FALLAR (falta el scope/ticket)
git commit -m "feat: prueba sin scope" --allow-empty

# Debe PASAR
git commit -m "feat(KEFA-XXX): prueba de commitlint" --allow-empty
```

Si el segundo pasó, deshaz ese commit de prueba (era solo para validar, no es trabajo real):

```bash
git reset --soft HEAD~1
```

Si **ninguno de los dos casos se comporta como se espera** (por ejemplo, el commit inválido no falla), el hook no está activo — repite el paso 3 antes de seguir. No sigas trabajando sin esta validación funcionando: es la única barrera automática que impide commits fuera de la convención del proyecto.

---

## 5. Antes de empezar a trabajar en algo

**Nunca trabajes directo sobre `develop` ni sobre `main`** — ambas están protegidas (requieren Pull Request y aprobación, no aceptan push directo). Las reglas de `main` se modificaron recientemente: consulta `docs/deployment/git-workflow.md` para el detalle vigente.

```bash
git checkout develop
git pull origin develop
git checkout -b feature/KEFA-XXX-descripcion-corta
```

Reemplaza `KEFA-XXX` por el número real del ticket en Jira. No se crean ramas sin ticket ni por integrante — solo por tarea real.

---

## 6. Al abrir el Pull Request — el error más común que ya tuvimos

Cuando pushees tu rama y GitHub te muestre el link para crear el PR, **antes de dar clic en "Create pull request"**, revisa el selector superior:

```
base: develop  ←  compare: feature/KEFA-XXX-descripcion-corta
```

GitHub selecciona `main` como `base` por defecto (es la rama por defecto del repo). Si no lo cambias manualmente a `develop`, tu PR se va a fusionar en el lugar equivocado — esto ya nos pasó una vez y tomó varios pasos revertirlo.

Con GitHub CLI, evita este error por completo especificando el `--base` explícitamente:

```bash
gh pr create --base develop --head feature/KEFA-XXX-descripcion-corta \
  --title "feat(KEFA-XXX): descripción breve" \
  --body "Ver checklist del PR template."
```

---

## 7. Si el link de comparación de GitHub te da 404

Verifica primero los datos reales de tu repo, no asumas la URL:

```bash
git remote -v
git branch -r
```

Construye el link de comparación con esos valores exactos:

```
https://github.com/<usuario-u-org>/<repo>/compare/develop...feature/KEFA-XXX-descripcion-corta
```

Un 404 casi siempre es un nombre de usuario, repo o rama mal escrito (GitHub distingue mayúsculas/minúsculas).

---

## 8. Después de que tu PR se fusiona

```bash
git checkout develop
git pull origin develop
git branch -d feature/KEFA-XXX-descripcion-corta
```

Antes de borrar cualquier rama (local o remota), confirma que sí está fusionada — no asumas:

```bash
git branch -r --merged origin/develop
```

Si tu rama aparece en esa lista, es seguro borrarla. Si `git branch -d` (minúscula) se niega con "not fully merged" pero ya confirmaste lo anterior con `--merged`, puedes forzar con `-D` mayúscula — pero solo después de esa confirmación, nunca antes.

---

## 9. Levantar el entorno de desarrollo con Docker

> **Estado:** este flujo se basa en los archivos del repositorio, pero aún **no se verificó de punta a punta** (Jira KEFA-55 "En curso", subtarea KEFA-62 "Documentar comandos" pendiente). Si algo falla, avisa en el chat 08 (DevOps).

**Requisitos:** Docker con Compose v2 (`docker compose version`).

### Paso 1 — Variables de entorno

Los archivos reales (`.env`, `frontend/.env`) **no se versionan**; solo se versionan los `.example`.

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
```

Edita `.env` y reemplaza los `changeme-*` por valores reales (como mínimo `SECRET_KEY` y `N8N_ENCRYPTION_KEY`). No pegues claves reales en chats ni las subas a Git.

> **Importante:** si tu `.env` contiene la línea `POSTGRES_PASSWORD=...`, **bórrala**. La contraseña de Postgres va solo en el secret del paso 2; si ambas están definidas, el contenedor de Postgres se niega a arrancar (inconsistencia conocida de `.env.example`, ver `control-de-estado.md`, H9).

### Paso 2 — Secreto de PostgreSQL

La contraseña de Postgres va en un Docker secret, no en `.env`:

```bash
cp secrets/postgres_password.txt.example secrets/postgres_password.txt
```

Edita `secrets/postgres_password.txt` con la contraseña real (una sola línea). La carpeta `secrets/` está en `.gitignore`, salvo los archivos `*.example`.

### Paso 3 — Levantar los servicios

```bash
docker compose up --build
```

Servicios definidos en `docker-compose.yml`:

| Servicio | Contenedor | Puerto en el host |
|---|---|---|
| `db` (PostgreSQL 17) | `kefa-db` | 5432 |
| `n8n` | `kefa-n8n` | `N8N_PORT` (5678 por defecto) |
| `backend` (Django) | `kefa-backend` | **8080** (mapeado a 8000 dentro del contenedor) |
| `frontend` (Vite) | `kefa-frontend` | 5173 |

### Paso 4 — Comprobar que funciona

- Backend: abre `http://localhost:8080/api/health/`; debe responder `{"status": "ok"}`.
- Frontend: abre `http://localhost:5173`.
- n8n: abre `http://localhost:5678`.

### Notas importantes

- **Puerto del backend.** El compose publica el backend en `8080` porque en una máquina Windows del equipo el rango 7535-8034 está excluido por Hyper-V (se ve con `netsh interface ipv4 show excludedportrange protocol=tcp`). Por eso `VITE_API_URL` en `frontend/.env` debe apuntar al puerto **publicado** (`http://localhost:8080`), aunque `frontend/.env.example` indique `8000`. Es una inconsistencia conocida (ver `control-de-estado.md`, H5).
- **`VITE_API_URL` nunca debe apuntar a `backend`** (nombre de red interna de Docker): el navegador no puede resolverlo.
- **CORS.** `CORS_ALLOWED_ORIGINS` en `.env` debe incluir el origen del frontend (`http://localhost:5173`).
- **Base de datos de n8n.** El script `docker/postgres/init-n8n-db.sh` crea `n8n_db` solo la primera vez que se crea el volumen de Postgres. Si cambias la configuración después, recrea el volumen (`docker compose down -v`; **esto borra los datos locales**).
- **Pruebas del backend.** Con las dependencias instaladas y una base de datos disponible: `python backend/manage.py test config users -v 2`. Las pruebas del orquestador no necesitan base de datos: desde `backend/`, `python -m unittest orchestrator.tests -v`.
- Correr el backend **sin Docker** (`backend/.env` con `POSTGRES_HOST=localhost`) todavía no es un flujo oficial.

---

## Resumen de comandos que NO existen fuera de Git Bash (en Windows)

| Comando | Dónde funciona |
|---|---|
| `chmod` | Solo Git Bash / Linux / macOS. En PowerShell usa `git update-index --chmod=+x <archivo>` |
| `ls -l`, `cat`, `grep` | Solo Git Bash / Linux / macOS |

---

## Checklist rápido de esta guía

- [ ] Cloné el repo y cambié a `develop`
- [ ] Corrí `npm install`
- [ ] Confirmé `git config core.hooksPath` → `.husky`
- [ ] Probé un commit inválido (falló) y uno válido (pasó)
- [ ] Nunca trabajo directo sobre `main`/`develop`, siempre en `feature/KEFA-XXX-...`
- [ ] Verifico el `base:` del PR antes de crearlo
- [ ] Confirmo con `--merged` antes de borrar cualquier rama
- [ ] Copié `.env`, `frontend/.env` y `secrets/postgres_password.txt` desde sus `.example` y `docker compose up --build` levanta los 4 servicios
