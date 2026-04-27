# Plan de Acción — reload_Matrix

> **Estado actual:** ~65-70% completado. Módulos core funcionales e integrados. Pendientes: bugs críticos, seguridad, testing, funcionalidades complementarias.
> **Fecha de creación:** 1 de abril 2026

---

## Prioridad 1 — Bugs Críticos (Resolver inmediatamente)

### 1.1. Registrar router de inventario en `main.py`
- **Archivos:** `backend/app/main.py`
- **Problema:** `inventory` está importado (línea 10) pero NO registrado con `app.include_router()`. Ningún endpoint de inventario responde.
- **Acción:** Agregar `app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["inventory"])` después de la línea 31.

### 1.2. Eliminar `get_current_user` duplicado en `inventory.py`
- **Archivos:** `backend/app/api/v1/routers/inventory.py` (líneas 20-45)
- **Problema:** Reimplementa la función de autenticación en lugar de importar desde `deps.py`. Código duplicado y difícil de mantener.
- **Acción:** Eliminar la función local y usar `from app.api.v1.deps import get_current_user`.

### 1.3. Eliminar `get_current_user` duplicado en `auth.py`
- **Archivos:** `backend/app/api/v1/routers/auth.py` (líneas 85-110)
- **Problema:** Misma función duplicada al final del archivo. No se usa como dependencia pero genera confusión.
- **Acción:** Eliminar; la fuente única debe ser `deps.py`.

### 1.4. `get_current_user` en `auth.py` no verifica `is_active`
- **Archivos:** `backend/app/api/v1/routers/auth.py`, `backend/app/api/v1/deps.py`
- **Problema:** La función `get_current_user` en `auth.py` no verifica si el usuario está activo (`is_active`). Un usuario desactivado podría seguir autenticándose.
- **Acción:** Agregar validación `if not user.is_active: raise HTTPException(status_code=400, detail="Inactive user")`.

---

## Prioridad 2 — Seguridad (Resolver esta semana)

### 2.1. Refresh Tokens
- **Archivos:** `backend/app/core/security.py`, `backend/app/api/v1/routers/auth.py`, `backend/app/models/sql/user.py`, `frontend/src/services/api.js`, `frontend/src/store/modules/auth.js`
- **Problema:** Solo existe access token con expiración de 8 días. Si se roba, tiene validez prolongada. Sin mecanismo de renovación segura.
- **Acciones:**
  - Agregar `create_refresh_token()` en `security.py` (expiración 30 días, almacenado en BD con hash)
  - Endpoint `POST /api/v1/auth/token` retorna `{access_token, refresh_token, token_type}`
  - Endpoint `POST /api/v1/auth/refresh` para renovar access token usando refresh token
  - Endpoint `POST /api/v1/auth/logout` para invalidar refresh token
  - Modelo `User`: agregar campo `hashed_refresh_token` (nullable)
  - Frontend: interceptor en `api.js` — si recibe 401, intentar refresh automáticamente antes de redirigir a login

### 2.2. Políticas de Contraseñas Seguras
- **Archivos:** `backend/app/core/security.py`, `backend/app/api/v1/routers/auth.py`, `backend/app/schemas/user.py`
- **Problema:** No hay validación de complejidad de contraseña. Se acepta cualquier string.
- **Acciones:**
  - Función `validate_password_strength(password)`: mín. 8 caracteres, 1 mayúscula, 1 minúscula, 1 número, 1 carácter especial
  - Validar en endpoint `/register` antes de crear usuario
  - Agregar validación Pydantic en schema `UserCreate` con mensaje de error descriptivo

### 2.3. Secret Key por Defecto Inseguro
- **Archivos:** `backend/app/core/config.py` (línea 10)
- **Problema:** `SECRET_KEY` tiene valor hardcoded `"your-secret-key-here"`. Si no se configura `.env`, todos los tokens son vulnerables.
- **Acción:** En el `__init__` de `Settings`, validar que `SECRET_KEY` no sea el valor por defecto en producción. Generar error claro si no está configurado.

### 2.4. CORS Abierto (`allow_origins=["*"]`)
- **Archivos:** `backend/app/main.py` (línea 19), `backend/app/core/config.py`
- **Problema:** CORS permite cualquier origen. En producción expone la API a ataques CSRF.
- **Acciones:**
  - Agregar `ALLOWED_ORIGINS: str` en `config.py` con valor configurable por `.env`
  - Reemplazar `["*"]` por `settings.ALLOWED_ORIGINS.split(",")` en `main.py`

### 2.5. Exception Handlers Globales
- **Archivos:** `backend/app/main.py`
- **Problema:** No hay manejo centralizado de excepciones. Errores no controlados retornan stack traces o HTML en lugar de JSON.
- **Acciones:**
  - `@app.exception_handler(HTTPException)` — retornar formato JSON consistente `{"detail": "...", "status_code": ...}`
  - `@app.exception_handler(RequestValidationError)` — retornar errores de validación Pydantic formateados
  - `@app.exception_handler(Exception)` — handler genérico que loguea el error y retorna `{"detail": "Internal server error"}` con status 500

### 2.6. Logging Estructurado
- **Archivos:** `backend/app/main.py`, `backend/app/core/config.py`
- **Problema:** No hay logging configurado. No se registran accesos, errores ni operaciones críticas.
- **Acciones:**
  - Configurar `logging` con formato: `%(asctime)s | %(levelname)s | %(name)s | %(message)s`
  - Agregar `LOG_LEVEL` en `config.py`
  - Loguear: login exitoso/fallido, creación de facturas, asientos contables, cambios de stock, errores 500
  - En producción: output en formato JSON para integración con sistemas de monitoreo

### 2.7. Permisos Granulares por Módulo y Acción
- **Archivos:** `backend/app/models/sql/user.py`, `backend/app/api/v1/deps.py`, `backend/app/schemas/user.py`, todos los routers
- **Problema:** Solo existen roles (ADMINISTRADOR, CONTADOR, etc.) sin permisos por acción. No se puede dar acceso a "ver facturas" sin dar acceso a "eliminar facturas".
- **Acciones:**
  - Nuevo modelo `Permission` (id, name, module, action) con relación many-to-many User↔Permission
  - Tabla intermedia `user_permissions`
  - Nueva dependencia `require_permission(module, action)` en `deps.py`
  - Migración Alembic para crear tablas y poblar permisos por defecto según rol
  - Aplicar decorators en endpoints críticos (eliminar, modificar asientos, facturas)

### 2.8. Auditoría de Cambios (Audit Log)
- **Archivos:** `backend/app/models/sql/` (nuevo `audit_log.py`), `backend/app/core/` (decorator), todos los routers
- **Problema:** No hay registro de quién hizo qué cambio. Requerido por normativa DIAN y buenas prácticas de seguridad.
- **Acciones:**
  - Modelo `AuditLog`: id, user_id, company_id, action (CREATE/UPDATE/DELETE), entity_type, entity_id, old_values (JSON), new_values (JSON), timestamp, ip_address
  - Decorator `@audit_action(entity_type)` aplicable a endpoints
  - Aplicar en: facturas, asientos contables, socios, reparaciones, garantías
  - Endpoint `GET /api/v1/admin/audit-logs/` para consultar historial
  - Vista frontend en Panel de Administración

---

## Prioridad 3 — Funcionalidades Pendientes (Resolver esta semana)

### 3.1. Upload de Logo de Empresa
- **Archivos:** `backend/app/api/v1/routers/company.py`, `backend/app/core/config.py`, `backend/app/main.py`, `frontend/src/views/Company/SetupView.vue`
- **Problema:** Modelo `Company` tiene `logo_url` pero no hay endpoint para subir archivos.
- **Acciones:**
  - Endpoint `POST /api/v1/companies/{company_id}/logo` con `UploadFile`
  - Validar: tipo (image/jpeg, image/png), tamaño máx 2MB
  - Guardar en `uploads/logos/` con nombre único (UUID)
  - Configurar `UPLOAD_DIR` en `config.py`
  - Servir archivos estáticos desde `/uploads/` en `main.py`
  - Frontend: componente de upload con preview en SetupView

### 3.2. Creación de Usuario Admin en Setup Inicial
- **Archivos:** `backend/app/api/v1/routers/company.py`, `backend/app/schemas/company.py`, `frontend/src/views/Company/SetupView.vue`
- **Problema:** El wizard de configuración de empresa no crea el usuario administrador inicial. Hay que registrarlo por separado.
- **Acciones:**
  - Modificar `CompanyCreate` schema para incluir campo opcional `admin_user: UserCreate`
  - En `create_company`, si viene `admin_user`, crear usuario vinculado a la empresa en la misma transacción
  - Frontend: agregar sección de datos del admin en el wizard de setup

### 3.3. Notas Crédito y Débito (Documentos de Ajusto DIAN)
- **Archivos:** `backend/app/models/sql/invoicing.py`, `backend/app/schemas/invoicing.py`, `backend/app/services/invoicing_service.py`, `backend/app/services/accounting_service.py`, `backend/app/api/v1/routers/invoicing.py`, `frontend/src/views/Invoicing/`
- **Problema:** No hay modelo ni lógica para notas crédito/débito. Requeridas por DIAN para devoluciones, anulaciones y ajustes de facturas electrónicas.
- **Acciones:**
  - Modelo `CreditDebitNote`: id, original_invoice_id, type (CREDIT/DEBIT), reason, amount, cufe, xml_ubl, estado_dian, fecha_envio_dian
  - Schemas: `CreditNoteCreate`, `DebitNoteCreate`, `CreditNoteResponse`
  - Servicio: `create_credit_note()`, `create_debit_note()` con generación de CUFE y XML UBL
  - Servicio contable: `create_note_journal_entry()` — reversión parcial de ingresos/IVA
  - Endpoints: CRUD de notas, endpoint para enviar a DIAN
  - Frontend: vista para crear notas desde una factura existente, listado de notas

### 3.4. Conexión Real con DIAN (Facturación Electrónica)
- **Archivos:** `backend/app/services/electronic_billing_service.py`
- **Problema:** `send_to_dian()` es un stub que simula el envío. No conecta con los servicios web reales de la DIAN.
- **Acciones:**
  - Investigar y documentar endpoints SOAP/REST de la DIAN para ambiente de pruebas
  - Implementar firma digital del XML con certificado `.p12`/`.pfx`
  - Implementar envío real al servicio web de validación previa de la DIAN
  - Manejar respuesta: ACEPTADO, RECHAZADO, con motivos
  - Agregar configuración en `.env`: `DIAN_ENVIRONMENT` (test/production), `DIAN_CERT_PATH`, `DIAN_CERT_PASSWORD`
  - Mantener modo simulación como fallback configurable

---

## Prioridad 4 — Testing (Resolver esta semana)

### 4.1. Configurar Infraestructura de Testing
- **Archivos:** `backend/tests/conftest.py`, `backend/requirements.txt`, `backend/pyproject.toml` (nuevo)
- **Acciones:**
  - Agregar dependencias: `pytest`, `pytest-asyncio`, `httpx`, `pytest-cov`, `factory-boy`
  - `conftest.py`: fixtures para `db_session` (con rollback), `test_client`, `test_user`, `test_company`, `auth_headers`
  - Configurar `pyproject.toml` con sección `[tool.pytest.ini_options]`
  - Script en `package.json` o Makefile para ejecutar tests

### 4.2. Backend — Tests Unitarios
- **Archivos:** `backend/tests/unit/`
- **Tests a crear:**
  - `test_security.py`: verify_password, create_access_token, validate_password_strength, create_refresh_token
  - `test_accounting_service.py`: crear asiento contable, validar débitos=créditos, libro mayor con saldos, declaración IVA, retenciones
  - `test_inventory_service.py`: deduct_stock (éxito y error por stock insuficiente), check_stock_availability, adjust_stock_level
  - `test_partner_service.py`: validación NIT/DV con algoritmo Modulo 11 (casos válidos e inválidos)
  - `test_electronic_billing.py`: generación CUFE (hash determinista), estructura XML UBL
  - `test_wallet_service.py`: deposit, withdraw (éxito y saldo insuficiente), transfer

### 4.3. Backend — Tests de Integración
- **Archivos:** `backend/tests/integration/`
- **Tests a crear:**
  - `test_auth.py`: flujo completo register → login → refresh → access protected endpoint → logout → token inválido
  - `test_invoicing.py`: crear factura con items → verificar descuento de inventario → verificar asiento contable automático
  - `test_repair.py`: crear orden → agregar items → cambiar estado a READY → generar factura → verificar inventario descontado → verificar asiento contable
  - `test_repair_warranty.py`: reparación con garantía → verificar que NO genera ingreso → verifica que SÍ registra costo de inventario
  - `test_accounting.py`: crear asiento con débitos≠créditos → error 400, crear asiento válido → publicar → verificar libro mayor cuadra
  - `test_company.py`: crear empresa → verificar plan de cuentas por defecto creado (30+ cuentas)

### 4.4. Cobertura Objetivo
- Meta: ≥80% en servicios y routers
- Ejecutar con: `pytest --cov=app --cov-report=term-missing --cov-report=html`

---

## Prioridad 5 — Docker y DevOps (Resolver próximo sprint)

### 5.1. Health Checks en Docker Compose
- **Archivos:** `docker-compose.yml`
- **Problema:** El plan menciona health checks pero no están configurados. `depends_on` solo espera a que el contenedor inicie, no a que el servicio esté listo.
- **Acciones:**
  - Backend: `test: ["CMD", "curl", "-f", "http://localhost:8000/"]`
  - DB: `test: ["CMD-SHELL", "pg_isready -U user -d business_db"]`
  - Frontend: `test: ["CMD", "curl", "-f", "http://localhost:80/"]`
  - Cambiar `depends_on` a usar `condition: service_healthy`

### 5.2. Variables de Entorno Seguras
- **Archivos:** `.env`, `.env.example`, `.gitignore`
- **Acciones:**
  - Crear `.env` con valores por defecto (SECRET_KEY generado con `openssl rand -hex 32`)
  - Crear `.env.example` como template público sin secretos reales
  - Verificar que `.env` esté en `.gitignore`

### 5.3. Dockerfile Backend — Mejoras
- **Archivos:** `backend/Dockerfile`, `backend/.dockerignore` (nuevo)
- **Acciones:**
  - Verificar multi-stage build si aplica
  - Ejecutar como non-root user
  - Crear `.dockerignore` con: `__pycache__/`, `.pytest_cache/`, `.env`, `*.pyc`, `tests/`

### 5.4. CI/CD Pipeline
- **Archivos:** `.github/workflows/ci.yml` (nuevo)
- **Acciones:**
  - Workflow que ejecute en cada push/PR:
    - Lint con Ruff
    - Tests con pytest
    - Build de Docker images
  - Notificación de resultados

---

## Prioridad 6 — Frontend: Pulido y Completitud (Resolver próximo sprint)

### 6.1. Módulo de Reparaciones — Store Vuex
- **Archivos:** `frontend/src/store/modules/repair.js` (nuevo), `frontend/src/services/api.js`
- **Problema:** `RepairView.vue` existe pero no tiene módulo de store dedicado. Probablemente hace llamadas directas o incompletas.
- **Acciones:**
  - Crear módulo Vuex con: state (orders, currentOrder, warranties, technicians), actions (fetchOrders, createOrder, updateStatus, generateInvoice, fetchWarranties, fileClaim), mutations
  - Agregar métodos de API en `api.js` para todos los endpoints de repair

### 6.2. Módulo de Facturación — Store Vuex
- **Archivos:** `frontend/src/store/modules/invoicing.js` (nuevo)
- **Problema:** No existe módulo de store para facturación.
- **Acciones:**
  - Crear módulo Vuex con: state (invoices, currentInvoice, items), actions (fetchInvoices, createInvoice, createInvoiceWithItems, sendToDian, getInvoiceXml), mutations
  - Agregar métodos de API en `api.js`

### 6.3. Módulo de Contabilidad — Store Vuex (Completar)
- **Archivos:** `frontend/src/store/modules/accounting.js`
- **Problema:** El módulo actual solo tiene CRUD básico de plan de cuentas y asientos. Faltan las acciones para los nuevos reportes.
- **Acciones:**
  - Agregar actions: `fetchLibroMayor`, `fetchLibroVentas`, `fetchLibroCompras`, `fetchDeclaracionIVA`, `fetchRetenciones`, `fetchIngresos`, `fetchPatrimonio`

### 6.4. Utilidades Compartidas
- **Archivos:** `frontend/src/utils/formatters.js` (nuevo), `frontend/src/utils/validators.js` (nuevo)
- **Acciones:**
  - `formatters.js`: formato moneda COP (`$ 1.234.567`), formato fechas colombianas (`DD/MM/YYYY`), formato NIT con DV (`900.123.456-7`)
  - `validators.js`: validación NIT con Modulo 11, validación email, campos requeridos, longitud mínima

### 6.5. Integración Visual de Estado DIAN
- **Archivos:** `frontend/src/views/Invoicing/InvoicingView.vue`
- **Acciones:**
  - Mostrar estado DIAN con badges de color (BORRADOR=gris, ENVIADO=azul, ACEPTADO=verde, RECHAZADO=rojo)
  - Botón "Enviar a DIAN" en facturas en estado BORRADOR
  - Mostrar CUFE en detalle de factura
  - Mostrar motivo de rechazo si aplica

---

## Prioridad 7 — Funcionalidades Adicionales (Backlog)

| # | Feature | Descripción | Esfuerzo |
|---|---|---|---|
| 7.1 | i18n | Configurar `vue-i18n` en frontend (es/en). Archivos de traducción para todos los textos de UI. | Medio |
| 7.2 | Escáner de barras con cámara | Integrar `html5-qrcode` o `quagga` en frontend para escanear códigos de barras desde cámara web/móvil. | Medio |
| 7.3 | Programa de lealtad | Extender wallet con sistema de puntos/acumulados por compras. Canje de puntos por saldo. | Alto |
| 7.4 | Límites de crédito | Campo `credit_limit` en Partner. Validación al facturar: bloquear si deuda > límite. | Bajo |
| 7.5 | Estado de Resultados | Nuevo método en `AccountingService`: ingresos - costos - gastos = utilidad neta. Vista frontend. | Medio |
| 7.6 | Balance General | Nuevo método en `AccountingService`: activos = pasivos + patrimonio. Vista frontend con gráfico. | Medio |
| 7.7 | Umbral 27 UVT | Validación en retenciones: no aplicar Retefuente si base diaria < 27 UVT. Configurar valor UVT anual. | Bajo |
| 7.8 | Retefuente bienes (10%) | Distinguir bienes vs servicios en retenciones. Servicios=2.5%, Bienes=10%. | Bajo |
| 7.9 | Control de rangos DIAN | Tabla `dian_billing_ranges` con desde/hasta, resolución, fecha vencimiento. Validar al crear factura. | Medio |
| 7.10 | Estado de Resultados | Nuevo método en `AccountingService`: ingresos - costos - gastos = utilidad neta. Vista frontend. | Medio |
| 7.11 | Formulario 350 | Generar archivo para declaración de renta según formato DIAN. | Alto |

---

## Resumen Ejecutivo

| Prioridad | Categoría | Items | Esfuerzo Total | Impacto |
|---|---|---|---|---|
| **1** | Bugs Críticos | 4 | Bajo (1-2h) | 🔴 Crítico |
| **2** | Seguridad | 8 | Alto (3-5 días) | 🔴 Crítico |
| **3** | Funcionalidades Pendientes | 4 | Alto (3-5 días) | 🟠 Alto |
| **4** | Testing | 4 | Medio (2-3 días) | 🟠 Alto |
| **5** | Docker y DevOps | 4 | Bajo (1 día) | 🟡 Medio |
| **6** | Frontend: Pulido | 5 | Medio (2-3 días) | 🟡 Medio |
| **7** | Funcionalidades Adicionales | 11 | Variable (backlog) | 🟢 Bajo |

---

## Orden de Ejecución Recomendado

```
Semana 1: Prioridad 1 (Bugs) + Prioridad 2.1-2.4 (Seguridad básica)
Semana 2: Prioridad 2.5-2.8 (Seguridad avanzada) + Prioridad 3.1-3.2 (Funcionalidades básicas)
Semana 3: Prioridad 3.3-3.4 (Notas crédito/DIAN) + Prioridad 4 (Testing)
Semana 4: Prioridad 5 (Docker/DevOps) + Prioridad 6 (Frontend)
Semana 5+: Prioridad 7 (Backlog según necesidad del negocio)
```
