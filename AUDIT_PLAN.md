# Plan de Remediación — Auditoría Reload Matrix

Hallazgos consolidados de la auditoría de seguridad y lógica de negocio.
Severidad: **CRITICA / ALTA / MEDIA / BAJA**.

---

## Top: Criticos

### Seguridad Backend
- **C1 RBAC efectivamente roto** — `require_permission` solo se aplica a ~10 endpoints. Inventorio, tesoreria, wallet, reparaciones, facturacion (`/with-items/`), compras quedan abiertos a cualquier usuario autenticado (`deps.py:125-153`).
- **C3 Refresh token usable como access token** — `get_current_user` no valida el claim `type` (`security.py:45-69`, `deps.py:21-29`).
- **C4 Logout no revoca access token** — vive 8 dias (`auth.py:164-184`, `config.py:15`).
- **C5 Path traversal en subida de backup** — `filename` sin sanitizar (`admin.py:431-448`).
- **C6 RCE via restore de backup** — ZIP subido se ejecuta con `psql -f` (`backup_service.py:100-128`).
- **Reflected CORS en handler 500** — eco de `Origin` + `Allow-Credentials: true` (`main.py:166-178`).
- **Secrets hardcodeados** en scripts (`app/scripts/init_database.py`, `reset_database.sh`).
- **`/purchases/extract-from-pdf` sin `verify_company_membership`** (`purchases.py:59-81`).

### Logica de Negocio
- **`wallet_service.withdraw/deposit` no valida `amount > 0`** — cantidades negativas crean dinero (`wallet_service.py:74,177-188`).
- **`treasury.deposit/withdraw/transfer` sin `amount > 0` ni `with_for_update`** (`treasury_service.py:407-505,546-636`).
- **`cancel_invoice` devuelve stock dos veces** cuando viene de reparacion (`repair_service.py:361-376` + `invoicing_service.py:491-501`).
- **Commits internos rompen atomicidad** (`accounting_service.py:2693,2756,3043`).
- **`create_invoice_from_repair` deduce stock con `commit=True`** (`repair_service.py:610-614`).

### Seguridad Frontend
- **XSS stored via `v-html` en `RepairView`** — `highlightMatch` no escapa `text` (`RepairView.vue:50,53,338-343`).
- **XSS en `toast.innerHTML`** (`plugins/toast.js:27`).
- **Router sin guards por rol/permiso** (`router/index.js:255-289`).
- **`selectedCompanyId` no se limpia en logout** (`auth.js:77-90`).
- **Password en claro en `state.user` tras `register`** (`auth.js:69`).
- **`console.log(res.data)` en LibroCompras** (`LibroComprasView.vue:138`).
- **`|| 1` fallback para `company_id`** en ~10 vistas contables.

### Infraestructura
- **`reset_database.sh` apunta a otro repo** (`Reload_Matrix_II`).
- **Backups en volumen `app_backups` en plaintext** accesible al container.
- **OpenAPI/Swagger publico en prod**.
- **CORS `["*"]` + credentials** en staging.
- **Sin headers de seguridad en nginx** (no CSP, no HSTS, no `X-Frame-Options`).

---

## Plan de remediación (orden por impacto)

### Bloque 1 — Auth Hardening (completado)
1. Agregar `type:"access"` a access tokens (`security.py`).
2. Rechazar `type == "refresh"` en `get_current_user` (`deps.py`).
3. Reducir `ACCESS_TOKEN_EXPIRE_MINUTES` de 8 dias (11520) a 30 min (`config.py`).
4. Agregar `jti` (uuid) a access tokens.
5. Tabla `revoked_tokens` + check en `get_current_user`.
6. `logout` revoca `jti` del access token (junto con el refresh).
7. Frontend `auth.js`: enviar `access_token` en logout y limpiar `selectedCompanyId`.

### Bloque 2 — RBAC granular (completado)
- Aplicar `require_permission(module, action)` en TODOS los routers.
- No bypassear permisos para tenant-superuser (solo platform-admin sin `company_id`).
- Seed `scripts/init_permissions.py` expandido con matriz CRUD por modulo.
- `/purchases/extract-from-pdf` ahora usa `verify_company_membership` (audit C1).
- Fix extra: bug preexistente en `UserMeResponse.populate_additional_fields` que
  mutaba `user.permissions` con strings y rompia la sesion SQLAlchemy.

### Bloque 3 — Sanitizacion Backups (completado)
- `_resolve_backup_path`: `Path.name` + `resolve()` dentro de `backup_dir`.
- Eliminado `/backups/upload` (y UI frontend); DR via volumen/S3 + restore de listados.
- `_safe_extract` anti Zip Slip en restore.
- Tests: `tests/unit/test_backup_service.py`.

### Bloque 4 — Validaciones Monetarias
- `amount > 0` en wallet/treasury.
- `with_for_update` en transfer.

### Bloque 5 — Atomicidad transaccional
- Parametro `commit: bool = False` en todos los services.
- Eliminar commits internos en `accounting_service`.

### Bloque 6 — XSS Frontend
- Escapar HTML en `highlightMatch` o cambiar `v-html` por `v-text` + `<mark>`.
- `textContent` en toast.

### Bloque 7 — Tenant context frontend
- Limpiar `selectedCompanyId` en `auth/logout` y en interceptor 401.
- Quitar `|| 1` fallback.

### Bloque 8 — Router guards por permiso + cleanup state.user
- Guards por rol/permiso en `router/index.js`.
- `delete userData.password` antes de comitear al store.

### Bloque 9 — CORS / Prod hardening
- No hacer eco de `Origin` en handler 500.
- Rechazar `["*"]` + credentials.
- `docs_url=None`, headers nginx, rotar secrets commiteados (git filter-repo), encryptar backups.