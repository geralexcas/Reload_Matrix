# Reload Matrix - Guia para Agentes de IA

## Resumen del Proyecto

Reload Matrix es un sistema ERP (Enterprise Resource Planning) para tiendas de tecnologia y talleres de reparacion en Colombia. Es un monorepo con backend Python/FastAPI y frontend Vue.js 3, orquestado con Docker Compose.

**Modulos principales:**
- Inventario (productos, control de stock, categorias, codigos de barras)
- Facturacion (facturas de venta, impresion POS termica, facturacion electronica DIAN)
- Reparaciones (ordenes de servicio, seguimiento de estados, asignacion de tecnicos, garantias)
- Terceros (clientes/proveedores unificados, validacion NIT/DV colombiano - Modulo 11)
- Tesoreria y Billetera (cajas registradoras, cuentas bancarias, transferencias, conciliacion bancaria, cheques)
- Contabilidad avanzada (PUC colombiano, asientos automaticos, libro diario, balance de prueba, libros de ventas/compras, declaraciones de IVA, retenciones, balance general, estado de resultados)
- Gestion de empresa (multi-tenant basico, resolucion DIAN)
- Panel de admin (usuarios, backups, logs de auditoria)
- Integracion IA (Google Gemini API)

**Stack tecnologico:**
- Backend: Python 3.11, FastAPI, SQLAlchemy 2.0, PostgreSQL 15, Alembic, Pydantic v2
- Frontend: Vue 3 (Options API), Vuex 4, Vue Router 4, Axios, vue-i18n, Vue CLI 5
- Infraestructura: Docker Compose, nginx (reverse proxy), GitHub Actions CI

## Comandos de Compilacion y Ejecucion

### Docker Compose (metodo principal)
```bash
docker-compose up --build                    # Construir e iniciar todo
docker compose up -d --build backend         # Reconstruir solo backend
docker compose up -d --build frontend        # Reconstruir solo frontend
docker compose exec backend python scripts/create_admin.py       # Crear admin
docker compose exec backend python scripts/init_database.py      # Inicializar DB
docker compose exec backend python scripts/init_permissions.py   # Inicializar permisos
./reset_database.sh                          # Reset completo (destruye datos)
```

### Backend (standalone)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend (standalone)
```bash
cd frontend
npm ci              # Instalar dependencias (limpio)
npm run serve       # Servidor de desarrollo
npm run build       # Build de produccion
```

### Migraciones de Base de Datos
```bash
# Dentro del contenedor backend
alembic upgrade head                              # Aplicar migraciones
alembic revision --autogenerate -m "descripcion"  # Generar nueva migracion
```

### Puertos de Servicio
| Servicio | Puerto Host | Puerto Contenedor |
|----------|-------------|-------------------|
| Frontend (nginx) | 8081 | 80 |
| Backend (FastAPI) | 8001 | 8000 |
| PostgreSQL | 5434 | 5432 |

## Comandos de Prueba

### Backend (pytest)
```bash
cd backend
pytest                                          # Ejecutar todas las pruebas
pytest -v                                       # Verbose
pytest --cov=app --cov-report=term-missing      # Con cobertura (requerido: >=80%)
pytest tests/unit/                              # Solo pruebas unitarias
pytest tests/integration/                       # Solo pruebas de integracion
pytest tests/unit/test_security.py              # Un archivo especifico
```

**Configuracion de pruebas** (`backend/pyproject.toml`):
- Framework: pytest con httpx (TestClient)
- DB de prueba: SQLite en memoria (StaticPool), no PostgreSQL
- Cobertura minima: 80% (`fail_under = 80`)
- Fixtures en `tests/conftest.py`: `db_session`, `client`, `test_company`, `test_user`, `auth_headers`

### Frontend
No existen pruebas frontend configuradas actualmente.

### Linting
```bash
cd backend && ruff check app/                   # Linter Python (ruff)
cd frontend && npm run lint                     # ESLint para Vue
cd frontend && npm run lint -- --no-fix         # ESLint sin auto-corregir
```

## Estructura del Proyecto

```
Reload_Matrix/
├── .env.example              # Template de variables de entorno
├── .github/workflows/ci.yml  # Pipeline CI (GitHub Actions)
├── docker-compose.yml        # Orquestacion de servicios
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt      # Dependencias Python
│   ├── pyproject.toml        # Config pytest + coverage
│   ├── alembic.ini           # Config Alembic
│   ├── alembic/versions/     # Migraciones de BD (8 archivos)
│   ├── scripts/              # Scripts de inicializacion (DB, admin, permisos)
│   ├── tests/
│   │   ├── conftest.py       # Fixtures de prueba
│   │   ├── unit/             # test_security, test_partner_service, test_inventory_service, test_electronic_billing
│   │   └── integration/      # test_auth
│   └── app/
│       ├── main.py           # Punto de entrada FastAPI
│       ├── core/             # config.py, database.py, security.py, audit.py, scheduler.py
│       ├── api/v1/routers/   # auth, accounting, admin, company, dashboard, inventory, invoicing, partners, purchases, repair, treasury, users, wallet
│       ├── models/sql/       # Modelos SQLAlchemy (ORM)
│       ├── schemas/          # Esquemas Pydantic v2
│       └── services/         # Logica de negocio (capa de servicio)
├── frontend/
│   ├── Dockerfile            # Multi-stage: node:16-alpine -> nginx:stable-alpine
│   ├── nginx.conf            # Reverse proxy (/api/ -> backend:8000)
│   ├── package.json
│   ├── .eslintrc.js
│   ├── vue.config.js
│   └── src/
│       ├── main.js           # Bootstrap de Vue (store, router, toast, i18n)
│       ├── services/api.js   # Instancia Axios con interceptores (token, refresh)
│       ├── router/           # Vue Router con guards de autenticacion
│       ├── store/modules/    # Vuex modules (auth, accounting, company, inventory, invoicing, partners, purchases, repair, treasury, wallet)
│       ├── views/            # Vistas por modulo
│       ├── components/       # Componentes reutilizables
│       ├── i18n/locales/     # es.js (default), en.js
│       ├── utils/            # formatters.js (COP, fechas, NIT), validators.js (NIT/DV Modulo 11)
│       └── plugins/          # toast.js (notificaciones personalizadas)
└── uploads/                  # Directorio de subida de archivos
```

## Directrices de Estilo de Codigo

### Backend (Python/FastAPI)

**Patron de arquitectura:** Service Layer
- Routers -> manejan HTTP, delegan a servicios
- Services -> logica de negocio (instanciados con sesion `db`)
- Models -> clases SQLAlchemy ORM
- Schemas -> clases Pydantic v2 BaseModel

**Nomenclatura:**
- Archivos: `snake_case.py` (ej: `accounting_service.py`, `chart_of_accounts.py`)
- Clases: `PascalCase` (ej: `AccountingService`, `JournalEntry`)
- Funciones/metodos: `snake_case` (ej: `create_product`, `deduct_stock`)
- Constantes: `UPPER_SNAKE_CASE` (ej: `NAMESPACE_UBL`, `SQLALCHEMY_DATABASE_URL`)
- Tablas SQLAlchemy: `snake_case` plural (ej: `chart_of_accounts`, `journal_entries`)

**Imports:**
- Orden: stdlib -> terceros -> locales
- Imports locales con alias de modulo: `from app.models.sql import user as user_model`
- Schemas: `from app.schemas import inventory as inv_schema`
- Servicios: `from app.services import inventory_service`

**Pydantic v2:**
- Usar `model_config = {"from_attributes": True}` (NO `class Config`)
- Usar `field_validator` y `model_validator` (NO `@validator`)
- Usar `model_dump()` (NO `.dict()`)

**Base de datos:**
- SQLAlchemy declarativo con `Column()` explicito
- Valores monetarios: `Numeric(15, 2)` (pesos colombianos COP)
- Enums: tipos PostgreSQL ENUM
- `company_id` en casi todos los modelos (multi-tenant)
- Timestamps: `created_at`/`updated_at` con `server_default=func.now()`

**Manejo de errores:**
- Services lanzan `ValueError` para errores de negocio
- Routers capturan y convierten a `HTTPException`
- Handlers globales en `main.py` (RequestValidationError, Exception generico)

**Autenticacion/autorizacion:**
- `Depends()` injection: `get_current_user`, `get_current_active_user`, `get_current_superuser`
- `require_permission(module, action)` para RBAC granular
- `verify_company_membership()` para aislamiento multi-tenant

**Idioma:** Codigo en ingles; comentarios y documentacion en espanol (contexto colombiano)

### Frontend (Vue.js 3)

**Arquitectura:** Vuex 4 + Vue Router + vue-i18n
- Componentes usan **Options API** (NO `<script setup>`)
- State management: Vuex con modulos namespaced
- API: instancia Axios centralizada (`src/services/api.js`)

**Nomenclatura:**
- Views: `PascalCaseView.vue` (ej: `RepairDetailView.vue`, `BankAccountsView.vue`)
- Componentes: `PascalCase.vue` (ej: `ProductForm.vue`, `BarcodeScanner.vue`)
- Store modules: `camelCase.js` (ej: `accounting.js`, `treasury.js`)
- CSS: `kebab-case` y `snake_case` mezclado

**Token storage:** `sessionStorage` (NO localStorage - se limpia al cerrar pestana)

**Internacionalizacion:** vue-i18n con espanol (`es`) como default, ingles (`en`) como fallback

**Utilidades colombianas:**
- `utils/formatters.js`: formato COP, fechas colombianas, NIT con DV
- `utils/validators.js`: validacion NIT, calculo DV (Modulo 11)

## Instrucciones de Prueba

### Al escribir nuevas pruebas backend:
1. Usar fixtures de `conftest.py` (`client`, `auth_headers`, `test_user`, `test_company`, `db_session`)
2. Las pruebas usan SQLite en memoria, no necesitan PostgreSQL
3. Cada prueba obtiene una DB limpia (function-scoped fixtures)
4. Nombres de archivos: `test_<modulo>.py`, clases: `Test<Modulo>`, funciones: `test_<escenario>`
5. Para endpoints protegidos, usar fixture `auth_headers` en las requests
6. Mantener cobertura >= 80%

### Ejemplo de prueba unitaria:
```python
def test_create_product(client, auth_headers):
    response = client.post("/api/v1/inventory/", json={...}, headers=auth_headers)
    assert response.status_code == 200
```

### Al crear nuevas migraciones:
1. Crear/modificar el modelo en `app/models/sql/`
2. Importar el modelo en `alembic/env.py`
3. Ejecutar `alembic revision --autogenerate -m "descripcion"`
4. Verificar el archivo generado en `alembic/versions/`
5. Probar con `alembic upgrade head`

## Consideraciones de Seguridad

### Variables de Entorno
- **NUNCA** commitear `.env` al repositorio (esta en `.gitignore`)
- Copiar `.env.example` y llenar valores reales en cada entorno
- `SECRET_KEY` es obligatoria en produccion (generar con `openssl rand -hex 32`)
- `GEMINI_API_KEY` y `DIAN_CERT_PASSWORD` son secretos que deben protegerse

### Autenticacion
- JWT con HS256, access token: 8 dias, refresh token: 30 dias
- Passwords hasheados con bcrypt (passlib)
- Validacion de fortaleza: min 8 chars, mayuscula, minuscula, digito, caracter especial
- Refresh tokens hasheados y almacenados en DB; logout invalida el refresh token

### RBAC
- Roles: ADMINISTRADOR, CONTADOR, TECNICO, VENDEDOR, BODEGUERO, FACTURADOR
- Permisos granulares por modulo + accion (many-to-many con usuarios)
- Superusuarios bypassean verificacion de permisos
- `verify_company_membership()` asegura aislamiento multi-tenant

### Auditoria
- `AuditLog` registra: usuario, empresa, accion (CREATE/UPDATE/DELETE/LOGIN/LOGOUT), entidad, valores anteriores/nuevos, IP
- Decorador `@audit_action(entity_type)` para logging automatico

### CORS
- Configurado via `ALLOWED_ORIGINS` (separados por coma)
- Si no se configura, fallback a `["*"]` (riesgo potencial - siempre configurar en produccion)

### Docker
- Backend ejecuta como usuario no-root (`appuser`)
- `.dockerignore` excluye `.env`, `*.db`, `.git`, caches

### Precauciones al modificar codigo:
- **NUNCA** hardcodear secretos, passwords ni API keys en el codigo fuente
- Validar siempre `company_id` para asegurar aislamiento entre empresas
- Usar parametros SQL (SQLAlchemy ORM lo hace por defecto) - nunca concatenar strings para queries
- El password default `admin123` en `init_database.py` es debil pero se establece directamente como hash (bypassea validacion) - solo para seeding inicial
- No implementar rate limiting actualmente - considerar agregarlo

## CI/CD

Pipeline en `.github/workflows/ci.yml` se ejecuta en push/PR a `main` y `develop`:

| Job | Que hace | Bloqueante |
|-----|----------|------------|
| backend-lint | `ruff check app/` | Si |
| backend-test | `pytest --cov=app --cov-report=term-missing -v` con PostgreSQL 15 | Si |
| backend-build | `docker build -t reload-matrix-backend .` (depende de lint+test) | Si |
| frontend-build | `npm ci` + `npm run lint` + `npm run build` | Lint no bloqueante |

**Nota:** El lint del frontend usa `|| true` (no bloqueante). Considerar hacerlo bloqueante.

## Convenciones Adicionales

### Al agregar un nuevo modulo backend:
1. Crear modelo en `app/models/sql/<modulo>.py`
2. Importar modelo en `app/models/sql/__init__.py` y en `alembic/env.py`
3. Crear schemas en `app/schemas/<modulo>.py`
4. Crear servicio en `app/services/<modulo>_service.py`
5. Crear router en `app/api/v1/routers/<modulo>.py`
6. Registrar router en `app/main.py`
7. Generar migracion: `alembic revision --autogenerate -m "add_<modulo>"`
8. Agregar pruebas en `tests/unit/test_<modulo>.py`

### Al agregar un nuevo modulo frontend:
1. Crear vista en `src/views/<Modulo>/`
2. Crear componente en `src/components/<Modulo>/`
3. Crear store module en `src/store/modules/<modulo>.js` y registrarlo en `src/store/index.js`
4. Agregar ruta en `src/router/index.js` con meta `requiresAuth`
5. Agregar traducciones en `src/i18n/locales/es.js` y `en.js`
6. Agregar item en sidebar (`src/components/layout/SidebarNav.vue`)

### Formato de commits:
- Usar espanol o ingles consistentemente dentro del equipo
- Formato sugerido: `<tipo>: <descripcion>` (ej: `feat: modulo de compras`, `fix: validacion NIT`)

### Moneda y localizacion:
- Todas las cantidades monetarias estan en Pesos Colombianos (COP)
- UVT 2026: $49.738 (configurado en `settings.UVT_VALUE`)
- Formato de fecha colombiano: DD/MM/YYYY
- NIT: numero + digito de verificacion (DV) calculado con Modulo 11
