#!/usr/bin/env sh
set -e

# config/settings.py lee POSTGRES_PASSWORD como variable de entorno
# plana (os.getenv("POSTGRES_PASSWORD")); no soporta el sufijo _FILE
# que usa el resto del stack (KEFA-ADR-004). Este entrypoint cierra
# esa diferencia sin tocar el código Python: lee el Docker secret
# montado y lo exporta como POSTGRES_PASSWORD antes de arrancar.
if [ -n "${POSTGRES_PASSWORD_FILE:-}" ] && [ -f "$POSTGRES_PASSWORD_FILE" ]; then
  export POSTGRES_PASSWORD="$(cat "$POSTGRES_PASSWORD_FILE")"
fi

exec "$@"
