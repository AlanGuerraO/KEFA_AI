#!/bin/bash
# Se ejecuta automáticamente por la imagen oficial de postgres al crear
# el volumen por primera vez (docker-entrypoint-initdb.d).
#
# Crea una base de datos separada para las tablas internas de n8n
# (n8n_db), dentro del mismo servidor Postgres del proyecto, en vez de
# mezclarlas con el esquema de la app (KEFA-ADR-004). Reutiliza el
# mismo usuario ya definido en POSTGRES_USER.

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE n8n_db OWNER $POSTGRES_USER;
EOSQL
