# Plan: Crear usuarios desde el TenantDetailView con `is_superuser`

## Contexto

El panel de Platform-Admin (`/platform/tenants/{id}`) muestra los usuarios de una empresa pero no permite crear nuevos. Se necesita un formulario para que el platform-admin cree usuarios en cualquier tenant, con la opcion de marcarlos como administrador de la empresa (tenant-superuser).

---

## Backend — `app/api/v1/routers/admin.py` (`create_user`, lineas 65-111)

Cambios minimos al endpoint `POST /api/v1/admin/users/`:

1. **Linea 73**: Cambiar `Depends(get_current_superuser)` → `Depends(get_current_platform_admin)` — alinearlo con el resto del panel de plataforma (Fase 0 dejo `get_current_platform_admin` en `deps.py:71`)
2. **Linea ~81**: Agregar `is_superuser = user_data.get("is_superuser", False)` — leer el campo del body
3. **Linea 105**: Reemplazar el hardcoded `is_superuser=False` por la variable `is_superuser`

Resultado: el platform-admin puede crear usuarios normales (`is_superuser=False`) o tenant-admins (`is_superuser=True`) en cualquier empresa, pasando `company_id` en el body.

**Import》：** Importar `get_current_platform_admin` en `admin.py` (reemplazar o complementar el import de `get_current_superuser` si ya no se usa en otros endpoints del archivo).

### Verificar uso de `get_current_superuser` en el resto de `admin.py`

Antes de quitar el import, revisar si otros endpoints del archivo (`update_user`, `toggle_user_active`, `delete_user`, `reset_user_password`, `list_permissions`, `create_permission`, backups, etc.) siguen usando `get_current_superuser`. Si es asi, mantener ambos imports.

---

## Frontend — `src/views/Platform/TenantDetailView.vue`

### Seccion de usuarios (linea ~75)

1. **Boton "+ Crear Usuario"** junto al titulo `h3` (linea 76)
2. **Formulario modal/inline** con toggle `showCreateUser`:
   - `username` — texto, requerido
   - `email` — email, requerido
   - `full_name` — texto, requerido
   - `password` — password, requerido (min 8, mayuscula, minuscula, numero, caracter especial — validacion del backend)
   - `role` — select: ADMINISTRADOR, CONTADOR, TECNICO, VENDEDOR, BODEGUERO, FACTURADOR (default VENDEDOR)
   - `is_superuser` — checkbox "Es administrador de la empresa" (default desmarcado)
3. El `company_id` se inyecta automaticamente desde `this.tenantId` — el usuario no lo ve
4. **Submit** → `dispatch('admin/createUser', { ...form, company_id: tenantId })` → refresca lista (`fetchUsers()`) → resetea formulario
5. **Errores** — mostrar `err.response.data.detail` (ej: "Email or username already exists", mensaje de fortaleza de password)
6. **CSS** — reutilizar las clases existentes (`.tenant-form`, `.form-row`, `.form-group`, `.btn-primary`, etc.)

### Data nueva

```js
showCreateUser: false,
createForm: {
  username: '',
  email: '',
  full_name: '',
  password: '',
  role: 'VENDEDOR',
  is_superuser: false
},
creatingUser: false,
createError: null
```

### Methods nuevos

- `createUser()` — valida campos, dispatch al store, refresca lista, resetea form
- `resetCreateForm()` — limpia el formulario

---

## Store — `src/store/modules/admin.js`

**Sin cambios.** El store ya tiene `createUser` (lineas 107-116) que envia el payload completo al endpoint. Funciona tal cual.

---

## Tests — `tests/integration/test_platform_admin_panel.py`

Agregar 3 tests:

1. **Platform-admin crea usuario normal** (`is_superuser=False`) en tenant → 201, usuario aparece en lista
2. **Platform-admin crea tenant-admin** (`is_superuser=True`) en tenant → 201, `is_superuser=True` en la respuesta
3. **Tenant-superuser intenta crear usuario** → 403 (ahora que cambiamos a `get_current_platform_admin`)

---

## Checkpoint

- `pytest --cov=app` >= 80%
- `ruff check app/` limpio en archivos modificados
- Frontend compila sin errores (`docker compose up -d --build frontend`)
- Verificar manualmente: login como platform-admin → listar tenants → entrar a un tenant → crear usuario → validar que aparece en la lista

---

## Resumen de archivos

| Archivo | Tipo | Cambio |
|---|---|---|
| `backend/app/api/v1/routers/admin.py` | Mod | `create_user`: leer `is_superuser` del body, cambiar dep a `get_current_platform_admin` |
| `frontend/src/views/Platform/TenantDetailView.vue` | Mod | Boton "+ Crear Usuario" + formulario con `is_superuser` checkbox |
| `backend/tests/integration/test_platform_admin_panel.py` | Mod | 3 tests nuevos de creacion de usuario |

**No se necesitan:** archivos nuevos, migraciones, cambios en store, ni cambios en schemas (el endpoint ya acepta `dict` sin validar con `UserCreate`).

---

## Orden de ejecucion

1. Backend: modificar `admin.py` (endpoint `create_user`)
2. Tests backend: agregar 3 tests a `test_platform_admin_panel.py`
3. Copiar al contenedor y ejecutar `pytest`
4. Frontend: modificar `TenantDetailView.vue` (boton + formulario + methods)
5. Reconstruir frontend (`docker compose up -d --build frontend`)
6. Verificar lint (`ruff check` en backend, build de frontend)
7. Checkpoint final