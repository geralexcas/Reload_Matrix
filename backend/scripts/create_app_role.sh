#!/usr/bin/env bash
# Crea el rol `appuser` (NO superuser, NO BYPASSRLS) para que la app conecte
# sin poder bypassar Row-Level Security.  El superuser `${POSTGRES_USER}`
# (creado por POSTGRES_USER/POSTGRES_PASSWORD) queda para migraciones Alembic
# y para BACKUP_DATABASE_URL (pg_dump necesita BYPASSRLS).
#
# Por que: los superusers de PostgreSQL bypassan RLS siempre, incluso con
# FORCE ROW LEVEL SECURITY.  Para que las politicas RLS (migracion
# 9f8e7d6c5b4a) realmente filtren, la app debe conectar como un rol no-superuser.
#
# Corre DENTRO del contenedor db (no requiere puerto expuesto al host, como en
# prod donde el DB no expone 5432).  Setea APP_DB_PASSWORD en .env primero:
#
#   APP_DB_PASSWORD=$(openssl rand -hex 16)
#   ./scripts/create_app_role.sh
#
# Despues, en .env confirma:
#   DATABASE_URL=postgresql://appuser:${APP_DB_PASSWORD}@db:5432/business_db
# y reinicia:  docker compose up -d --force-recreate backend
#
# Default: lee POSTGRES_USER/POSTGRES_DB del entorno de compose (.env).

set -euo pipefail

: "${APP_DB_PASSWORD:?APP_DB_PASSWORD es obligatorio (setealo en .env, NO lo commitees)}"
: "${POSTGRES_USER:=user}"
: "${POSTGRES_DB:=business_db}"
: "${POSTGRES_PASSWORD:=password}"

COMPOSE="${DOCKER_COMPOSE:-docker compose}"

echo "Creando rol appuser dentro del contenedor db (corre como superuser '${POSTGRES_USER}')..."

$COMPOSE exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<SQL
DO \$\$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'appuser') THEN
    CREATE ROLE appuser WITH LOGIN PASSWORD '${APP_DB_PASSWORD}' NOSUPERUSER NOBYPASSRLS;
    RAISE NOTICE 'Rol appuser creado.';
  ELSE
    ALTER ROLE appuser WITH LOGIN PASSWORD '${APP_DB_PASSWORD}' NOSUPERUSER NOBYPASSRLS;
    RAISE NOTICE 'Rol appuser ya existia; password/attrs actualizados.';
  END IF;
END \$\$;

-- appuser necesita DML (no DDL; las migraciones corren como '${POSTGRES_USER}').
GRANT CONNECT ON DATABASE "${POSTGRES_DB}" TO appuser;
GRANT USAGE ON SCHEMA public TO appuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO appuser;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO appuser;

-- Tablas futuras ( creadas por migraciones como '${POSTGRES_USER}') tambien accesibles a appuser.
ALTER DEFAULT PRIVILEGES FOR ROLE "${POSTGRES_USER}" IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO appuser;
ALTER DEFAULT PRIVILEGES FOR ROLE "${POSTGRES_USER}" IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO appuser;

-- Confirmar
SELECT rolname, rolsuper, rolbypassrls FROM pg_roles WHERE rolname = 'appuser';
SQL

echo "OK.  En .env confirma:"
echo "  DATABASE_URL=postgresql://appuser:\${APP_DB_PASSWORD}@db:5432/${POSTGRES_DB}"
echo "  BACKUP_DATABASE_URL=postgresql://${POSTGRES_USER}:\${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}"
echo "y reinicia:  docker compose up -d --force-recreate backend"