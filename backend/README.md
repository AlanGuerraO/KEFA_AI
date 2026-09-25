# Backend de KEFA AI

Backend desarrollado con Django y Django REST Framework.

## Instalación local en Windows (Git Bash)

Ejecutar desde la raíz del repositorio. Se necesita Python compatible
con las versiones indicadas en backend/requirements.txt y PostgreSQL
para las funciones que utilizan la base de datos.

```bash
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
```

## Variables de entorno

Crear backend/.env. No subir este archivo a Git.

Ejemplo para PostgreSQL instalado localmente:

```dotenv
SECRET_KEY=reemplazar-por-una-clave-generada
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=kefa_ai
POSTGRES_USER=kefa_user
POSTGRES_PASSWORD=reemplazar-por-la-contrasena-local
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Generar una clave con:

```bash
backend/.venv/Scripts/python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copiar el resultado en SECRET_KEY del archivo backend/.env.

La configuración también acepta DB_NAME, DB_USER, DB_PASSWORD,
DB_HOST y DB_PORT como nombres alternativos. Si ambas variantes
tienen valores, se priorizan las variables POSTGRES_*.

La plantilla de la raíz contiene variables para todo el sistema.
Su host PostgreSQL "db" está previsto para Docker; para una instalación
local se utiliza localhost.

## Estructura

- config/: configuración, rutas, endpoint de salud y pruebas iniciales.
- users/: modelo de usuario personalizado y endpoint del usuario actual.
- manage.py: comandos de administración.
- requirements.txt: dependencias fijadas.

## Verificación

```bash
backend/.venv/Scripts/python.exe backend/manage.py check
backend/.venv/Scripts/python.exe backend/manage.py test config
```

Las pruebas iniciales verifican que GET /api/health/ devuelve
HTTP 200 con {"status": "ok"} sin autenticación y que POST devuelve
HTTP 405. No acceden a PostgreSQL ni comprueban su conexión.

## Base de datos y ejecución

Crear previamente la base de datos y el usuario de PostgreSQL
indicados en backend/.env. Después ejecutar:

```bash
backend/.venv/Scripts/python.exe backend/manage.py migrate
backend/.venv/Scripts/python.exe backend/manage.py createsuperuser
backend/.venv/Scripts/python.exe backend/manage.py runserver
```

- Salud: http://127.0.0.1:8000/api/health/
- Administración: http://127.0.0.1:8000/admin/
- Usuario actual: http://127.0.0.1:8000/api/users/me/

El endpoint del usuario actual requiere autenticación. Se puede
comprobar en el navegador después de iniciar sesión en el administrador.
JWT todavía no está configurado.

El servidor runserver y DEBUG=True son para desarrollo local.

## Alcance

Esta base incluye configuración PostgreSQL y un modelo de usuario
personalizado que deberán revisarse también en sus tickets respectivos.
No implica que las tareas de PostgreSQL y autenticación estén completas.
