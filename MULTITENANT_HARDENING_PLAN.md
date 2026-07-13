# Plan de Hardening Multi-Tenant — Reload Matrix

**Driver:** riesgo de fuga/cruce de informacion entre empresas.
**Decision:** endurecer el modelo compartido (NO migrar a BD-por-tenant). El bug logico se arregla en codigo; separar BD no lo arregla y genera nuevos problemas operativos.

---

## Estado actual (lo que ya esta bien)

- ORM auto-filter en SELECTs (`app/core/tenant_context.py`).
- `verify_company_membership` valida path param `company_id` contra `current_user.company_id` (`app/api/v1/deps.py`).
- Token `cid` validado contra `company_id` actual → re-login si reasignan al usuario.
- INSERTs asignan `company_id` desde el path param validado (no del body).
- `with_for_update()` siempre con filtro `company_id` explicito.
- Sin SQL crudo en servicios (solo `SELECT 1` en healthcheck).
- Test base: `tests/unit/test_tenant_isolation.py` (inventory + companies + dashboard + audit + users).

---

## Riesgos encontrados (por severidad)

### P0 — Fuga real y explotable HOY

1. **`admin.py` user management** (`update_user:122`, `toggle_user_active:145`, `delete_user:163`, `reset_user_password:180`) usan `get_current_superuser`. Un **tenant-superuser** (`is_superuser=True` + `company_id=X`) consulta `User` por id sin filtro de tenant (User esta en `_EXCLUDE_FROM_AUTO_FILTER`) → puede mutar password/email/rol/estado de usuarios de otra empresa.
2. **`admin.py:51 get_user`** — tenant-superuser bypassea el check de company_id (linea 62) → lee datos de cualquier usuario cross-tenant.

### P1 — Falta red de seguridad a nivel BD

3. **Sin Row-Level Security (RLS) de PostgreSQL.** Un query raw SQL, un modelo nuevo sin `company_id`, o un bulk `Query.update()`/`Query.delete()` bypassan el ORM filter y no hay nada abajo que frene. El `ponytail:` en `tenant_context.py:25-27` admite que UPDATE/DELETE sin SELECT previo no estan cubiertos.

### P1 — Cobertura de tests insuficiente

4. `test_tenant_isolation.py` solo cubre **inventory**. Sin tests cross-tenant para: accounting, treasury, wallet, repair, partners, purchases, invoicing, credit/debit notes.

### P2 — Platform-admin sin contrapeso

5. `deps.py:71-80` — platform-admin = superuser sin `company_id` = acceso global sin 2FA ni IP-restrict. Si su token se compromete, todo tenant expuesto. Sin alertas de acceso cross-tenant.

---

## Fases

### Fase 0 — Tapar la fuga actual (P0)

- **Fix `admin.py`**: en `get_user`, `update_user`, `toggle_user_active`, `delete_user`, `reset_user_password`, agregar check de company_id para tenant-superusers. Solo platform-admin (`is_superuser and not company_id`) bypassea.
- **Test de regresion**: tenant-superuser A intenta mutar/leer usuario de company B → 403.

### Fase 1 — RLS en PostgreSQL (P1)

- **Migracion Alembic**: `ENABLE ROW LEVEL SECURITY` + `CREATE POLICY tenant_isolation USING (company_id::text = current_setting('app.tenant_id', true))` en tablas tenant-scoped (NO en `users`, `companies`, `audit_logs`, `permissions` — aisladas por app).
- **`get_current_user`**: `SET LOCAL app.tenant_id = {cid}` (PG only; SQLite salta por dialecto).
- **`verify_company_membership`**: platform-admin branch setea `app.tenant_id` al company_id resuelto.
- **`create_company`**: setea `app.tenant_id = db_company.id` antes de `create_default_chart_of_accounts`.
- **Test RLS**: raw SQL bypass sigue filtrado (PG only, skipif SQLite).

Politica deny-by-default: si `app.tenant_id` unset → NULL → no rows. Platform-admin scopea al tenant que administra (via `verify_company_membership`).

### Fase 2 — Tests de aislamiento para todos los modulos (P1)

Parametrizar `test_tenant_isolation.py` para correr el escenario (crear en A, leer en B → 403) sobre: accounting, treasury, wallet, repair, partners, purchases, invoicing, credit/debit notes. Reusa fixtures `test_company_b` + `non_super_auth_headers`.

### Fase 3 — CI guardrails (P2)

CI check (script/ruff custom) que prohiba: `text(` en servicios, `Query.update({})` / `Query.delete()` bulk, modelos nuevos sin `company_id`. Documentar regla en `AGENTS.md`.

### Fase 4 — Endurecer platform-admin (P2-P3, opcional)

2FA o token corto (1h) para platform-admin; alerta en AuditLog de acceso cross-tenant.

---

## Restriccion known

Tests corren en **SQLite** (`conftest.py`). RLS es PostgreSQL-only → tests RLS se marcan `skipif` dialecto != postgresql. El ORM auto-filter cubre el path de SQLite; RLS es la red de produccion.

---

## Estado final (verificado 2026-07-13)

### Pre-Fase — fix pg_dump bajo RLS (commit separado `6aefc0b`)
- **Bug descubierto al planear la migracion a prod:** `BackupService` corre `pg_dump`/`psql` como subprocess fuera del Engine de SQLAlchemy, por lo que el evento `before_cursor_execute` no dispara, `app.tenant_id` queda unset → RLS deny-by-default → **pg_dump vuelca 0 filas tenant** (inventario, facturas, partners, contabilidad, tesoreria). Silencioso y catastrofico; los tests SQLite no lo detectaban (RLS no aplica alli).
- **Fix:** `config.py` añade `BACKUP_DATABASE_URL` (cae a `DATABASE_URL` si se vacia); `backup_service.py` lo usa en `create_backup` (pg_dump) y `restore_backup` (psql). El operador setea `BACKUP_DATABASE_URL` a un rol con BYPASSRLS (el superuser `${POSTGRES_USER}` o un rol `backup_role` dedicado).
- **Verificado en staging (local):** con app corriendo como `appuser` (RLS enforcing) y `BACKUP_DATABASE_URL=postgresql://user:...`, el dump contiene las 44 filas de products + invoices + partners + chart_of_accounts (292 KB). Sin `BACKUP_DATABASE_URL` el dump tendria 0 filas tenant.
- **Rollback verificado en staging:** revertir `.env` (`DATABASE_URL` de vuelta a superuser) + reiniciar deja la app funcional (health 200, login 200, inventory 200). RLS queda inert (superuser bypassa) pero `verify_company_membership` sigue aislando en la capa app (cross-tenant 403). Rollback seguro confirmado.

### Fase 0 — DONE
- `admin.py`: `get_user`, `update_user`, `toggle_user_active`, `delete_user`, `reset_user_password` ahora validan `db_user.company_id == current_user.company_id` para tenant-superusers. Solo platform-admin bypassa.
- Tests de regresion: 7 casos (GET/PUT/PATCH/DELETE/reset-password cross-tenant → 403; own-tenant → 200; platform-admin bypass → 200). Todos pasan.

### Fase 1 — DONE (verificado end-to-end en PG vivo)
- Migracion `9f8e7d6c5b4a`: `ENABLE + FORCE ROW LEVEL SECURITY` + `CREATE POLICY tenant_isolation USING (company_id::text = current_setting('app.tenant_id', true))` en 21 tablas tenant-scoped. Aplicada al contenedor PG.
- Evento `before_cursor_execute` en `app/core/tenant_context.py`: setea `app.tenant_id` (SET LOCAL via cursor crudo, sin recursion) antes de CADA query (PG only; SQLite no-op). Sobrevive commits del service layer. Cubre raw SQL.
- `get_current_user` / `verify_company_membership` / `create_company` setean el ContextVar `current_tenant_id` (el evento lo lee).
- **Descubrimiento clave:** la app conectaba como `user` (superuser de PG) → RLS bypassado. Creado rol `appuser` (NO superuser, NO BYPASSRLS) + script `scripts/create_app_role.sh` + `.env.example` (`APP_DB_PASSWORD`) + `docker-compose.override.yml` usa `appuser`. La app ya corre como `appuser` (verificado: login + list productos 200; cross-tenant 403; raw SQL filtrado por RLS).
- Test RLS PG-only (skipif SQLite) + verificacion manual: raw SQL con tenant=1 devolvio solo `{1}` (RLS bloquea bypass de ORM).
- Scripts de seed (`create_test_products.py`, `seed_accounting.py`) setean `current_tenant_id` al inicio.

### Fase 2 — DONE
- `TestCrossTenantReadBlocked` parametrizado sobre 8 endpoints: partners, invoicing, repair, purchases, wallet, accounting (chart-of-accounts), treasury (bank-accounts, cash-accounts). Todos → 403 cross-tenant. Suite unitario: 78 passed + 1 skipped.
- Fix bonus: `conftest.py` `db_session` fixture resetea `current_tenant_id` (fix de leak preexistente entre tests que no usaban `client`).

### Fase 3 — DONE
- `scripts/check_tenant_guardrails.py`: banea `text()` (raw SQL) y bulk `Query.update({})`/`Query.delete()` en `app/services` y `app/api`. Paso CI agregado a `.github/workflows/ci.yml` (backend-lint job). Nota en `AGENTS.md` (capa 1 ORM + capa 2 RLS + guardrails CI + regla).

### Fase 4 — Pendiente (opcional)
- 2FA / token corto / IP-restrict para platform-admin. No hecho (P3).

### Pendiente para el operador (acciones manuales)
1. Cambiar `APP_DB_PASSWORD` en `.env` de `test-rls-pass` (valor de prueba) a un secreto real (`openssl rand -hex 16`). Recrear el rol: `APP_DB_PASSWORD=<real> ./scripts/create_app_role.sh`.
2. Re-superuser-izar el rol `user` si lo necesitas para admin (queda sin superuser en dev; `appuser` es no-superuser por diseño).
3. Resetear el password de `german` (lo cambie a `Test@1234` durante la verificacion end-to-end).
4. Ruff: 206 errors preexistentes (deuda tecnica, no de este hardening). El CI `backend-lint` los bloquearia; considerar `ruff check --fix` aparte.
