# Comandos de Docker — KEFA AI

Referencia de comandos para trabajar con el entorno de Docker del proyecto (ticket KEFA-55 / subtarea KEFA-62).

**Última actualización:** 12 de octubre de 2026 · **Responsable:** Alan (chat 08 — DevOps e Infraestructura)

> **Leyenda de verificación**
> - ✅ Ejecutado en este proyecto durante KEFA-007 y funcionó.
> - ⚠️ Comando estándar de Docker/Postgres, **todavía no ejecutado en este proyecto**. Probar antes de depender de él.

Para el **primer arranque paso a paso** (crear `.env`, secretos, migraciones) ve `primeros-pasos-clonar-repo.md`, sección 9. Para **síntomas y soluciones**, la sección 9.7 de esa guía. Este documento es la referencia de comandos del día a día.

---

## 0. Convenciones

| Elemento | Valor |
|---|---|
| Servicios (`docker-compose.yml`) | `db`, `n8n`, `backend`, `frontend` |
| Contenedores | `kefa-db`, `kefa-n8n`, `kefa-backend`, `kefa-frontend` |
| Puertos en el host | `db` 5432 · `n8n` 5678 · `backend` `${BACKEND_HOST_PORT:-8000}` (interno 8000) · `frontend` 5173 |
| Red | `kefa-network` |
| Volúmenes | `postgres_data`, `n8n_data` (en Docker aparecen con el prefijo del proyecto, p. ej. `proyecto_ia_kefa_postgres_data`; el prefijo sale del nombre de la carpeta: confírmalo con `docker volume ls`) |
| Secreto | `secrets/postgres_password.txt` (nunca se versiona) |

- Todos los comandos se ejecutan **desde la raíz del repo** (donde está `docker-compose.yml`).
- Se usa `docker compose` (v2, con espacio), no `docker-compose`.
- En **Git Bash (Windows)**, antepón `MSYS_NO_PATHCONV=1` a los comandos que lleven una ruta que empiece con `/` (ver sección 10).

---

## 1. Ciclo diario

| Quiero… | Comando | |
|---|---|---|
| Levantar todo en segundo plano | `docker compose up -d` | ✅ |
| Levantar reconstruyendo imágenes | `docker compose up -d --build` | ✅ |
| Levantar solo algunos servicios | `docker compose up -d db n8n` | ✅ |
| Ver el estado (todos deben estar `Up`, `db` además `healthy`) | `docker compose ps` | ✅ |
| Ver también contenedores detenidos o caídos | `docker compose ps -a` | ⚠️ |
| Detener sin borrar contenedores | `docker compose stop` | ⚠️ |
| Volver a arrancar lo detenido | `docker compose start` | ⚠️ |
| Reiniciar un servicio | `docker compose restart frontend` | ⚠️ |
| Bajar todo (conserva los datos) | `docker compose down` | ✅ |

`docker compose up -d` también **recrea** los contenedores cuyo `docker-compose.yml` o `.env` cambió; no hace falta bajarlos antes.

---

## 2. Qué hago cuando cambié algo

| Cambié… | Hago… | Motivo |
|---|---|---|
| `backend/requirements.txt` | `docker compose up -d --build backend` | Las dependencias se instalan al construir la imagen |
| `backend/Dockerfile` o `docker-entrypoint.sh` | `docker compose up -d --build backend` | Forman parte de la imagen |
| `frontend/package.json` | `docker compose up -d --build frontend` | Igual: `npm install` corre al construir |
| `frontend/Dockerfile` | `docker compose up -d --build frontend` | Forma parte de la imagen |
| `.env` (raíz) | `docker compose up -d` | Los contenedores leen `.env` al crearse |
| `frontend/.env` | `docker compose restart frontend` | Vite lo lee al arrancar |
| `docker-compose.yml` | `docker compose up -d` | Recrea lo que cambió |
| `secrets/postgres_password.txt` | Ver sección 6 (recrear volumen) | Postgres guarda la contraseña **al crear el volumen** |
| `docker/postgres/init-n8n-db.sh` | Ver sección 6 (recrear volumen) | Solo corre al crear el volumen por primera vez |
| Código de `backend/` (`.py`) | Normalmente nada: el `./backend` está montado y `runserver` recarga solo ⚠️ | Si no recarga, `docker compose restart backend` |
| Código de `frontend/src/` | Normalmente nada: Vite recarga solo ⚠️ | En Windows, el bind-mount puede no propagar los eventos de archivo; si no recarga, habría que activar *polling* en `vite.config.js` (código del frontend) |

Reconstruir **sin caché** (si sospechas una capa vieja):

```bash
docker compose build --no-cache backend     # ⚠️
docker compose up -d backend
```

---

## 3. Logs y diagnóstico

```bash
docker compose logs backend                  # ✅ todo el log de un servicio
docker compose logs --tail=100 backend       # ⚠️ solo las últimas 100 líneas
docker compose logs -f backend               # ⚠️ seguir en vivo (Ctrl+C para salir)
docker compose logs n8n | grep -i deprecat   # ✅ filtrar con grep
```

Más comprobaciones:

```bash
# Estado de salud de la base de datos
docker inspect --format "{{.State.Health.Status}}" kefa-db      # ⚠️  → healthy

# ¿En qué puerto del host quedó publicado el backend?
docker compose port backend 8000                                # ⚠️

# ¿El frontend alcanza al backend POR LA RED INTERNA de Docker?
# (aquí sí se usa el nombre del servicio y el puerto interno)
docker compose exec frontend wget -qO- http://backend:8000/api/health/   # ⚠️  → {"status":"ok"}

# Validar sintaxis del compose sin levantar nada
docker compose config --quiet                                   # ⚠️
```

Desde **tu navegador o `curl`** el backend se alcanza por `localhost:<BACKEND_HOST_PORT>`; desde **otro contenedor**, por `backend:8000`. No se mezclan.

---

## 4. Comandos de Django

### `run --rm` vs `exec` — cuál usar

| | `docker compose run --rm backend …` | `docker compose exec backend …` |
|---|---|---|
| Qué hace | Crea un contenedor **nuevo y temporal** y pasa por el *entrypoint* | Abre un proceso nuevo dentro del contenedor **que ya corre** |
| ¿Tiene `POSTGRES_PASSWORD`? | **Sí** (el entrypoint la exporta desde el secreto) | **No**: ese proceso no hereda lo que exportó el entrypoint |
| Úsalo para | `migrate`, `createsuperuser`, `makemigrations`, `test`, `shell` | Inspeccionar archivos o variables del contenedor que ya corre |

Por eso, **todo lo que toque la base de datos va con `run --rm`**. Usar `exec` produce `password authentication failed`.

```bash
docker compose run --rm backend python manage.py check             # ⚠️
docker compose run --rm backend python manage.py migrate           # ✅
docker compose run --rm backend python manage.py makemigrations    # ⚠️
docker compose run --rm backend python manage.py createsuperuser   # ✅
docker compose run --rm backend python manage.py changepassword <usuario>   # ⚠️
docker compose run --rm backend python manage.py test config users # ⚠️
docker compose run --rm backend python manage.py shell             # ⚠️
```

Si `createsuperuser` rechaza la contraseña por "demasiado corta/común", **no aceptes el bypass**: usa una contraseña real (`openssl rand -base64 16`).

Comprobar que el entrypoint exporta la contraseña **sin imprimirla**:

```bash
docker compose run --rm backend python -c "import os; print(bool(os.environ.get('POSTGRES_PASSWORD')))"   # ⚠️  → True
```

---

## 5. Base de datos (PostgreSQL)

El usuario es `kefa_user` (valor de `POSTGRES_USER`). Dentro del contenedor la conexión es local, por eso **no pide contraseña**.

```bash
# Listar bases de datos: deben aparecer kefa_ai y n8n_db
MSYS_NO_PATHCONV=1 docker compose exec db psql -U kefa_user -d kefa_ai -c "\l"     # ✅

# Listar tablas de Django / de n8n
docker compose exec db psql -U kefa_user -d kefa_ai -c "\dt"                       # ⚠️
docker compose exec db psql -U kefa_user -d n8n_db -c "\dt"                        # ⚠️

# Sesión interactiva de psql (Git Bash: si dice "the input device is not a TTY", antepón winpty)
docker compose exec db psql -U kefa_user -d kefa_ai                                # ⚠️
```

Desde una herramienta externa (DBeaver, psql del host) conecta a `localhost:5432` con el usuario `kefa_user` y la contraseña de `secrets/postgres_password.txt`.

### Respaldo y restauración ⚠️

```bash
mkdir -p backups                                                    # la carpeta backups/ está en .gitignore

# Respaldar (dos bases: la de Django y la de n8n)
docker compose exec -T db pg_dump -U kefa_user kefa_ai > backups/kefa_ai.sql
docker compose exec -T db pg_dump -U kefa_user n8n_db  > backups/n8n_db.sql

# Restaurar (sobre una base vacía)
docker compose exec -T db psql -U kefa_user -d kefa_ai < backups/kefa_ai.sql
```

- Usa `-T` para que Docker no asigne TTY al redirigir la salida o la entrada.
- Los respaldos contienen **datos reales**: nunca se versionan.
- Un respaldo de `n8n_db` solo sirve si conservas la **misma `N8N_ENCRYPTION_KEY`**; con otra, las credenciales guardadas en n8n quedan inutilizables.

---

## 6. Volúmenes y reinicio limpio

| Quiero… | Comando | Efecto |
|---|---|---|
| Bajar todo **conservando datos** | `docker compose down` ✅ | Borra contenedores y red; los volúmenes se quedan |
| Bajar todo **y borrar los datos** | `docker compose down -v` ⚠️ | Borra `postgres_data` **y** `n8n_data` |
| Ver los volúmenes | `docker volume ls` ✅ | |
| Borrar **solo** el volumen de Postgres | `docker volume rm <proyecto>_postgres_data` ✅ (con el stack abajo) | Se reinicializa Postgres: se aplica la contraseña actual del secreto y vuelve a correr `init-n8n-db.sh` (crea `n8n_db`) |

**Cuándo hay que recrear el volumen de Postgres:**

- Cambiaste `secrets/postgres_password.txt` después de crear el volumen (`password authentication failed`).
- Corregiste `docker/postgres/init-n8n-db.sh` y `n8n_db` no existe.
- Cambias de versión mayor de Postgres (p. ej. 16 → 17).

Secuencia completa (**borra los datos de Postgres**; solo mientras no haya datos reales):

```bash
docker compose down
docker volume ls | grep postgres_data          # confirma el nombre exacto
docker volume rm proyecto_ia_kefa_postgres_data
docker compose up -d --build
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py createsuperuser
```

---

## 7. Secretos y variables

```bash
# Ver la configuración ya resuelta (variables sustituidas)
docker compose config                           # ⚠️
```

> ⚠️ `docker compose config` **imprime los valores reales** de tu `.env` (`SECRET_KEY`, `N8N_ENCRYPTION_KEY`, …). No pegues su salida en chats, issues ni PRs.

- Comprobar que el secreto está montado en un contenedor:
  `MSYS_NO_PATHCONV=1 docker compose exec backend ls -la /run/secrets/` ✅
- **No** imprimas el contenido de `/run/secrets/postgres_password` salvo que sea indispensable y en tu máquina local.
- Comprobar que un script no tiene finales de línea de Windows (CRLF): cada línea debe terminar en `$`, sin `^M`:
  `MSYS_NO_PATHCONV=1 docker compose exec backend cat -A /usr/local/bin/docker-entrypoint.sh` ✅
- Un `$` dentro de un valor de `.env` se escribe `$$` (si no, Compose lo toma como variable y avisa `"nu" variable is not set`).
- **No** definas `POSTGRES_PASSWORD` en `.env`: junto con `POSTGRES_PASSWORD_FILE` hace que Postgres no arranque.

---

## 8. Entrar a un contenedor

```bash
docker compose exec backend sh        # ⚠️  (si pide TTY en Git Bash: winpty docker compose exec backend sh)
docker compose exec frontend sh       # ⚠️  (imagen Alpine: solo `sh`, no `bash`)
docker compose exec db sh             # ⚠️
```

Salir: `exit`.

---

## 9. Limpieza de disco

```bash
docker image prune           # ⚠️ borra imágenes huérfanas ("dangling")
docker builder prune         # ⚠️ borra la caché de build
docker system df             # ⚠️ ver cuánto ocupa Docker
```

**Evita** `docker system prune -a --volumes`: borra imágenes y volúmenes de **todos** tus proyectos de Docker, no solo de KEFA AI.

---

## 10. Particularidades de Windows / Git Bash

| Problema | Causa | Solución |
|---|---|---|
| `ls: cannot access 'C:/Program Files/Git/run/secrets/'` | Git Bash (MSYS) convierte los argumentos que empiezan con `/` a rutas de Windows | `MSYS_NO_PATHCONV=1 docker compose exec …` (o duplicar la barra: `//run/secrets/`) |
| `bind: An attempt was made to access a socket in a way forbidden by its access permissions` | Hyper-V/WSL2 reserva rangos de puertos | `powershell.exe -Command "netsh interface ipv4 show excludedportrange protocol=tcp"` y elige un `BACKEND_HOST_PORT` **fuera de todos los rangos** (en una máquina del equipo estaba excluido `7535-8034`, así que ni `8000` ni `8001` servían; funcionó `8080`) |
| `chmod: command not found` | PowerShell no tiene `chmod` | Usar Git Bash, o `git update-index --add --chmod=+x <archivo>` |
| Un script de shell falla dentro del contenedor | Finales de línea CRLF | El repo fuerza `LF` con `.gitattributes`; si pasa, `git add --renormalize <archivo>` |
| `the input device is not a TTY` | Terminal de Git Bash sin TTY real | Anteponer `winpty` al comando |

---

## 11. Qué NO hacer

- **No** usar `docker compose exec` para `migrate` o `createsuperuser` (sin contraseña → `password authentication failed`).
- **No** borrar volúmenes (`down -v`, `volume rm`) si ya hay datos que importen y no tienes respaldo.
- **No** poner `POSTGRES_PASSWORD` en `.env`.
- **No** cambiar `N8N_ENCRYPTION_KEY` después de que n8n haya guardado credenciales.
- **No** versionar `.env`, `secrets/postgres_password.txt`, `backend/.env`, `frontend/.env` ni respaldos de `backups/`.
- **No** pegar la salida de `docker compose config` en lugares públicos.
- **No** fijar a todo el equipo un puerto que es un workaround de una sola máquina: se cambia en el `.env` local.

---

## Estado de esta documentación

- Los comandos marcados ✅ se ejecutaron con el stack completo (`db`, `n8n`, `backend`, `frontend`) en KEFA-007.
- Los marcados ⚠️ son comandos estándar pendientes de validar en el proyecto; al validarlos, cambiar su marca a ✅.
- Falta, para cerrar T-24/T-38 del Control de Estado: **probar el arranque desde un clon limpio** siguiendo `primeros-pasos-clonar-repo.md`.
