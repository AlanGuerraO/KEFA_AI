# Backend KEFA AI — Django + DRF
#
# Versión de Python alineada con el entorno local real del equipo:
# backend/.venv usa CPython 3.14 (confirmado en los .pyc de
# site-packages: *.cpython-314.pyc).

FROM python:3.14-slim

WORKDIR /app

# Instalar dependencias primero (cachea esta capa mientras no cambie
# requirements.txt, evitando reinstalar en cada build)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código de la app (.dockerignore excluye .env, .venv y basura local)
COPY . .

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["docker-entrypoint.sh"]

# Servidor de desarrollo (DEBUG=True, runserver). Para producción real
# se reemplazaría por un servidor WSGI como gunicorn — no se hace aquí
# para no adelantar una decisión de arquitectura no tomada todavía.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
