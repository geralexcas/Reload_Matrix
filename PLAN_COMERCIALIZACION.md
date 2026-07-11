# Plan: Opcion C — Multi-tenant compartido endurecido

## Decisiones fijadas

- **Onboarding**: manual en fase 1 (platform-admin da de alta cada cliente). Self-service + pago como meta de fase posterior (Fase 3).
- **Multi-empresa por usuario**: No. 1 usuario = 1 empresa (`company_id`). Company switcher del frontend se simplifica/quita. M:N postergado a futuro.
- **Base de datos en produccion**: Postgres en el mismo VPS con volumen + backup offsite.
- **Planes/pago en fase 1**: No. Primero se endurece seguridad y se vende manualmente. Plan/Subscription/Quota + pago en Fase 3.

---

## Diagnostico (estado actual)

- Aislamiento por columna `company_id` en ~20 modelos, **sin mixin/base compartido** (cada modelo declara `company_id` por separado, ej. `backend/app/models/sql/inventory.py:32`).
- Filtro de tenant **manual en cada servicio** (`service.get_products(company_id, ...)`). Si un servicio olvida filtrar, hay fuga.
- `verify_company_membership` (`backend/app/api/v1/deps.py:54-85`) valida que `user.company_id == company_id` (query param), pero el `company_id` llega **desde el cliente** y los superusers lo bypassean (`:59`).
- Endpoints abiertos: `POST /companies/` y `GET /companies/` sin auth (`backend/app/api/v1/routers/company.py:24,138`).
- Token JWT solo lleva `{"sub": username}` (`backend/app/core/security.py`), sin claim de tenant.
- Admin router (`backend/app/api/v1/routers/admin.py`) tiene scoping inconsistente: `get_audit_logs:213` solo filtra `if company_id:` (sin company_id -> retorna logs de todos los tenants).
- Deploy: uvicorn single-worker (`backend/Dockerfile:28`), credenciales hardcoded (`docker-compose.yml:9,42-43`), mounts en vivo (`:20`), rate limiter in-memory (`backend/app/main.py:38`).

**Riesgo real de comercializar hoy:** fuga de datos entre tenants (marcado como S1 critico en `INFORME_AUDITORIA.md:143` y `bugs_segunda_auditoria_Julio_8.md:1181`).

---

## Fase 0 — Fundamentos de seguridad (bloqueante para vender)

### 0.1 Aislamiento a nivel ORM (red de seguridad automatica)

**Objetivo:** que sea imposible leakage por un service que olvide filtrar.

- Crear `backend/app/models/sql/base.py` con `TenantMixin` exponiendo `company_id` + registry de entidades tenant.
- `backend/app/core/database.py`: event `do_orm_execute` + `with_loader_criteria` inyecta `Entity.company_id == current_tenant` en toda query de entidades tenant, excepto lista de exclusiones globales (`Company`, `Permission`, `User` para platform-admin paths, `AuditLog` global). `current_tenant` via `contextvars.ContextVar`.
- `backend/app/core/middleware.py` (nuevo): middleware que resuelve `company_id` del `current_user.company_id` y setea el contextvar por request.
- `backend/app/main.py`: registrar middleware + event.
- Migrar los ~10 modelos que declaran `company_id` ad-hoc a usar `TenantMixin`.

### 0.2 Endurecer autorizacion de tenant

- `backend/app/api/v1/deps.py:54-85` `verify_company_membership`: distinguir **platform-admin** (superuser sin `company_id`, ve todo) de **tenant-admin/superuser de tenant** (con `company_id`, limitado al suyo). Hoy cualquier superuser cruza a ciego (`:59`).
- `require_permission` (`:88-114`) ya bypassea superusers (`:93`): mismo criterio de platform-admin vs tenant-admin.
- Eliminar la confianza en `company_id` que llega del cliente como query param en los routers (~9): `inventory`, `invoicing`, `partners`, `wallet`, `treasury`, `repair`, `purchases`, `accounting`, `dashboard`. El `company_id` se lee del usuario autenticado. Platform-admin puede especificar `company_id` explicitamente.

### 0.3 Cerrar endpoints de company abiertos

- `backend/app/api/v1/routers/company.py:24` `POST /companies/`: requerir platform-admin (onboarding manual por ahora).
- `:138` `GET /companies/`: platform-admin ve todos; tenant-admin solo la suya.
- `:144` `GET /companies/{id}`: con `verify_company_membership`.

### 0.4 Fix scoping de admin

- `backend/app/api/v1/routers/admin.py:199` `get_audit_logs`: filtrar SIEMPRE por `current_user.company_id` para no-superuser; el `company_id` opcional solo para platform-admin.
- `:22` `list_users`: resolver el conflicto `company_id: Optional` vs `verify_company_membership(company_id: int)`.

### 0.5 Token con claim de tenant

- `backend/app/core/security.py` (create/decode): anadir/validar `"cid": user.company_id` en el payload del JWT.
- Divergencia `cid` vs `user.company_id` actual -> forzar re-login (token invalido).

### 0.6 Regression test cross-tenant

- `backend/tests/unit/test_tenant_isolation.py` (nuevo): 2 tenants con datos, asertar que desde tenant A no se ven los de B via todos los endpoints principales (inventory, invoicing, partners, repair, wallet, treasury, accounting, admin).
- Cobertura >= 80% intacta. `ruff check app/` limpio.

### Checkpoint Fase 0

- `pytest --cov=app --cov-report=term-missing` >= 80%, `ruff check app/` limpio, test cross-tenant verde.

---

## Fase 1 — Capacidad de vender manual

### 1.1 Onboarding admin-gated

- `POST /companies/` ya crea company + admin + PUC default en una transaccion (`backend/app/api/v1/routers/company.py:24-79`). Base buena. Envolver requiere platform-admin (Fase 0.3).
- Flujo: (a) das de alta el cliente via platform-admin, (b) el admin tenant se loguea via `/api/v1/auth/token`, (c) gestion normal.
- Vista de platform-admin separada del tenant-admin en frontend.

### 1.2 Simplificar frontend (1 user = 1 empresa)

- `frontend/src/components/layout/TopHeader.vue`: quitar el company switcher (o dejar read-only).
- `frontend/src/services/api.js:31-35`: dejar de inyectar `company_id` por query param (ahora viene del backend por usuario autenticado).
- `frontend/src/store/modules/company.js:15-19`: simplificar `selectedCompanyId` (quitar fallback a sessionStorage o dejar fijo).

### 1.3 Rate limiting distribuido

- `backend/app/main.py:38` slowapi in-memory -> `redis://` (requerido para >1 worker, ver Fase 2).
- Anadir dependencia `redis` en `backend/requirements.txt`.

---

## Fase 2 — Produccion

### 2.1 Docker prod

- `docker-compose.yml` -> split en `docker-compose.prod.yml`:
  - Quitar mount en vivo (`:20` `./backend/app:/app/app`).
  - Credenciales desde `.env` unicamente; eliminar override hardcoded (`:9` `DATABASE_URL=...`, `:42-43` `user/password`).
  - Backend: gunicorn + uvicorn workers (`--workers N`) en lugar de uvicorn single-worker (`backend/Dockerfile:28`).
- `docker-compose.override.yml` para dev (mounts en vivo, debug, single worker).

### 2.2 Edge / TLS

- Anadir Traefik o Caddy como reverse proxy con TLS automatico (Let's Encrypt). Nginx actual del frontend queda detras.
- Subdominios por cliente (cosmetic routing, no DB separada): middleware resuelve `company` por host header. Opcional, no bloqueeante.

### 2.3 Datos en el VPS

- Volumen `postgres_data` + cron de backup **offsite** (fuera del VPS — S3-compatible / Backblaze B2). El `BackupService` + `scheduler` ya existen (`backend/app/core/scheduler.py`); agregar upload a storage externo. El backup en el mismo disco del VPS no protege del fallo del disco.
- Secrets fuera del repo (`SECRET_KEY`, `GEMINI_API_KEY`, `DIAN_CERT_PASSWORD` — `.env` ya gitignored).
- Considerar Postgres gestionado (RDS/Supabase/Neon) cuando factures o tengas clientes que dependan de los datos. Mientras pocos clientes, VPS + backup offsite es aceptable.

### 2.4 Observabilidad

- Logs estructurados ya existen (`backend/app/main.py:29`). Centralizar destino (Loki/CloudWatch/Datadog — opcional).
- Healthcheck `/health` con dependencia de DB (ademas del `/` actual).

---

## Fase 3 — Self-service + pago (meta posterior)

### 3.1 Landing + registro self-service

- Landing publica, registro con **verificacion de email**.
- Modelo `EmailVerification` (token, expiracion). Nuevo modelo + endpoint de verificacion.

### 3.2 Plan / Subscription / Quota

- Modelo `Plan` (limite usuarios, productos, facturas/mes, storage en MB).
- Modelo `Subscription` (company_id, plan_id, estado `active|pending_payment|suspended|cancelled`, vigencia, fecha_inicio, fecha_fin).
- Middleware de quota: validar limite antes de create (usuarios, productos, facturas). Retornar 402/409 con mensaje claro.
- Superuser platform-admin puede overridear quota.

### 3.3 Pago (Wompi/PayU Colombia)

- Webhook de pago -> activa `Subscription`. El tenant se crea al confirmar pago (o modo trial pre-pago, configurable).
- Tenant en estado `pending_payment` no opera hasta activarse (middleware bloquea endpoints de negocio).
- Integrar Wompi (preferido para Colombia) o PayU. Webhook con verificacion de firma.

### 3.4 (Futuro) M:N user-companies

- Si despues decides atender contadores/agencias: tabla `user_companies` + re-emitir token al cambiar company. Se posterga por la eleccion del 1:1. Desbloquea el caso del contador que atiende 3 clientes.

---

## Resumen de archivos a tocar (Fase 0, la urgente)

| Archivo | Cambio |
|---|---|
| `backend/app/models/sql/base.py` (nuevo) | `TenantMixin` + registry de entidades tenant |
| `backend/app/core/database.py` | `do_orm_execute` event + contextvar tenant |
| `backend/app/core/middleware.py` (nuevo) | middleware que setea tenant context |
| `backend/app/main.py` | registrar middleware + event |
| `backend/app/api/v1/deps.py` | reescribir `verify_company_membership` (sin bypass a ciego); platform-admin vs tenant-admin |
| `backend/app/core/security.py` | claim `cid` en token |
| `backend/app/api/v1/routers/company.py` | auth en `GET`/`POST` |
| `backend/app/api/v1/routers/admin.py` | fix scoping de audit-logs y users |
| `~9 routers` (inventory, invoicing, partners, wallet, treasury, repair, purchases, accounting, dashboard) | `company_id` del usuario, no del query param |
| `~10 modelos` (inventory, invoicing, repair, partners, wallet, purchases, audit, credit_debit_notes, dian_billing, accounting) | usar `TenantMixin` en vez de `company_id` ad-hoc |
| `backend/tests/unit/test_tenant_isolation.py` (nuevo) | regression cross-tenant |

---

## Orden de ejecucion sugerido

1. **Fase 0** (una sola PR grande o 3 sub-PRs: ORM filter / deps+tokens / company+admin hardening + tests). Bloqueante.
2. **Fase 1** (onboarding admin-gated + simplificar frontend + redis limiter).
3. **Fase 2** (prod compose + TLS edge + backup offsite).
4. Vender manual.
5. **Fase 3** cuando se quiera escalar self-service + pago.