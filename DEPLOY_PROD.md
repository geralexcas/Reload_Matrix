# Deploy del Hardening Multi-Tenant a Produccion

Plan ejecutable para migrar el hardening (RLS + fix admin.py + guardrails) al
servidor de produccion (192.168.1.13, Cloudflare Tunnel) **sin perder datos**.

**Commits:** `6aefc0b` (fix pg_dump) + `2c7a482` (hardening) en `origin/master`.

**Verificado en staging (local):**
- RLS enforcing end-to-end (login propio 200, cross-tenant 403, raw SQL filtrado).
- Backup con `BACKUP_DATABASE_URL` contiene las 44 filas tenant + invoices/partners/contabilidad (292 KB). Sin ese fix el dump tendria 0 filas tenant.
- Rollback (revertir `.env` a superuser) deja la app funcional; cross-tenant sigue 403 por capa app.

---

## Riesgo critico resuelto antes de migrar

`BackupService` corre `pg_dump`/`psql` como subprocess **fuera** del Engine de
SQLAlchemy, por lo que el evento `before_cursor_execute` no dispara y `app.tenant_id`
queda unset. Tras el swap a `appuser` (no-superuser), RLS deny-by-default
filtraria **pg_dump a 0 filas tenant** — backup diario incompleto y silencioso.
Fix: `BACKUP_DATABASE_URL` (commit `6aefc0b`) apunta a un rol con BYPASSRLS.

---

## Bloque 1 — Validacion en staging (ya verificada en local, re-correr si staging es otro host)

Si staging es un host distinto de tu local, restaurar el backup de prod mas
reciente alli y repetir:

```bash
# 1. Restaurar backup de prod en el DB de staging
docker compose exec -T db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} < pre_rls_backup.sql

# 2. Aplicar migracion RLS
docker compose exec backend alembic upgrade head
docker compose exec backend alembic current    # confirmar 9f8e7d6c5b4a

# 3. Crear rol appuser dentro del contenedor db (no requiere puerto expuesto)
APP_DB_PASSWORD=$(openssl rand -hex 16) ./backend/scripts/create_app_role.sh

# 4. Setear .env de staging:
#    APP_DB_PASSWORD=<el de arriba>
#    DATABASE_URL=postgresql://appuser:${APP_DB_PASSWORD}@db:5432/${POSTGRES_DB}
#    BACKUP_DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}

# 5. Reconstruir backend
docker compose up -d --build --force-recreate backend

# 6. Smoke test
curl -o /dev/null -w "%{http_code}\n" http://localhost:8001/health   # 200
# login tenant-admin + listar inventario de su empresa -> 200
# listar inventario de OTRA empresa -> 403

# 7. BACKUP TEST (critico)
docker compose exec backend python -c "
from app.services.backup_service import BackupService
BackupService().create_backup()
print('backup ok')
"
# el dump debe contener filas tenant:
docker compose exec backend python -c \"
import zipfile, re
from pathlib import Path
bks = sorted(Path('backups').glob('backup_*.zip'))
with zipfile.ZipFile(bks[-1]) as z:
    data = z.open('database.sql').read().decode('utf-8','ignore')
m = re.search(r'COPY public\\\\.products.*?\\\\\\\\\\\\.\\\\n', data, re.DOTALL)
print('products rows en dump:', m.group(0).count(chr(10))-2 if m else 0)\"

# 8. Scan logs (24h)
docker compose logs --since 24h backend | grep -iE "tenant_id|row-level|permission denied|500" | head
```

## Bloque 2 — Deploy en produccion (ventana ~2-3 min)

**Avisar a usuarios: ventana breve (restart del backend).**

```bash
# 0. Backup full de prod AHORA (antes de tocar nada)
docker compose exec -T db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > pre_rls_backup_$(date +%Y%m%d_%H%M).sql
ls -lh pre_rls_backup_*.sql    # confirmar tamano razonable (no 0 bytes)

# 1. git pull (trae los 2 commits)
cd /ruta/Reload_Matrix
git pull origin master
git log --oneline -3    # confirmar 6aefc0b + 2c7a482 presentes

# 2. Aplicar migracion RLS (la app sigue como superuser -> RLS bypassed -> cero disrupcion)
docker compose exec backend alembic upgrade head
docker compose exec backend alembic current    # confirmar 9f8e7d6c5b4a
# Verificar politicas activas:
docker compose exec db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c \
  "SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class WHERE relname='products';"
#    relrowsecurity=t, relforcerowsecurity=t  -> OK

# 3. Crear rol appuser dentro del contenedor db (no disruptivo)
APP_DB_PASSWORD=$(openssl rand -hex 16) ./backend/scripts/create_app_role.sh
#    anotar este password para meterlo en .env

# 4. Actualizar .env de prod:
#    APP_DB_PASSWORD=<el de arriba>
#    DATABASE_URL=postgresql://appuser:${APP_DB_PASSWORD}@db:5432/${POSTGRES_DB}
#    BACKUP_DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
#    (usar un editor; .env esta en .gitignore, no se commitea)

# 5. Reconstruir backend (unico momento con disrupcion ~1 min; frontend y DB no se tocan)
docker compose up -d --build --force-recreate backend

# 6. Smoke test inmediato
curl -o /dev/null -w "%{http_code}\n" http://localhost:8001/health    # 200
# login como tenant-admin real -> 200
# GET /inventory/?company_id=<su_empresa> -> 200
# GET /inventory/?company_id=<otra_empresa> -> 403  (RLS ya enforcing)

# 7. Verificar backup post-deploy
docker compose exec backend python -c "from app.services.backup_service import BackupService; BackupService().create_backup(); print('ok')"
# el dump debe contener filas tenant (mismo chequeo del Bloque 1.7)

# 8. Resetear password de 'german' si quedó con Test@1234 (solo si dev/prod comparten DB; en prod no aplica)
```

## Bloque 3 — Monitoreo post-deploy (24h)

```bash
docker compose logs --since 24h -f backend | grep -iE "tenant_id|row-level|permission denied|invalid input|500"
# Confirmar que el backup programado (24h scheduler) corrio sin error
docker compose logs --since 48h backend | grep -i "copia de seguridad"
# Confirmar login de al menos un usuario de cada empresa real
```

---

## Rollback (si algo falla)

**Rapido (~1 min) — deja la app funcional:**
```bash
# Revertir .env de prod:
#   DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
# (BACKUP_DATABASE_URL puede quedar apuntando al superuser tambien)
docker compose up -d --force-recreate backend
# La app reconecta como superuser -> RLS bypassed -> app funcional.
# RLS sigue armado en BD pero sin efecto; verify_company_membership sigue aislando en app.
```

**Completo (solo si el rapido no basta):**
```bash
docker compose exec backend alembic downgrade -1    # remueve politicas RLS
```

**Datos (solo si hubo corrupcion):**
```bash
cat pre_rls_backup_YYYYMMDD_HHMM.sql | docker compose exec -T db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}
```

---

## Riesgos / desconocidos abiertos

1. **Endpoints no probados bajo RLS enforcing**: cualquier path que toque tablas tenant sin pasar por `get_current_user`/`verify_company_membership` (sin `current_tenant_id` seteado) devolveria 0 filas. `auth/refresh`, `auth/logout` tocan `users` (sin RLS, ok). El Bloque 3 (scan logs) los captura. Si aparece, fix: setear `current_tenant_id` en ese path o sacar la tabla de RLS.
2. **`prevent_invoice_delete` trigger + RLS** coexisten (override via `session_replication_role='replica'` bypassa ambos). Sin impacto.
3. **Colision de nombres `appuser`**: OS user del contenedor (`Dockerfile:11`, uid 1000) vs PG role `appuser`. Son distintos; el gosu OS user NO implica bypass de RLS (lo da el rol PG, no el OS user).
4. **CI no corre en `master`** (solo `main`/`develop`): el guardrail `check_tenant_guardrails.py` depend de ejecucion manual pre-commit. Correr antes de cada push futuro: `python backend/scripts/check_tenant_guardrails.py`.
5. **`german` password `Test@1234`** en dev local (no prod): resetear si el dev es compartido.

---

## Pendiente para el operador (acciones manuales)

- [ ] Generar `APP_DB_PASSWORD` real con `openssl rand -hex 16` (no `test-rls-pass`).
- [ ] Setear en `.env` de prod: `APP_DB_PASSWORD`, `DATABASE_URL` (appuser), `BACKUP_DATABASE_URL` (superuser).
- [ ] Ejecutar Bloque 1 en staging real (si staging != local) o confiar en la verificacion local ya hecha.
- [ ] Ejecutar Bloque 2 en prod.
- [ ] Monitorear Bloque 3 por 24h.
- [ ] Resetear `german` password si dev compartido.

## Pre-Fase: fix pg_dump (commit 6aefc0b, ya merged)

- `config.py` añade `BACKUP_DATABASE_URL` (cae a `DATABASE_URL`).
- `backup_service.py` lo usa en `create_backup` (pg_dump) y `restore_backup` (psql).
- `.env.example` documenta `BACKUP_DATABASE_URL`.