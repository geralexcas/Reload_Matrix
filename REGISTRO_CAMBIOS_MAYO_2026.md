# Registro de Cambios - Mayo 2026

## Resumen General
Este documento registra todas las modificaciones realizadas al sistema Reload Matrix II durante Mayo 2026.

---

## 1. Corrección de Errores Críticos

### 1.1 Selector de Cuentas Contables Vacío
**Problema:** Al crear cuentas de caja en Tesorería, el selector de cuentas contables aparecía vacío.

**Solución:**
- Modificado `CashAccountsView.vue` para usar `sessionStorage.getItem('selectedCompanyId')` directamente en mounted
- Esto asegura que el companyId esté disponible al momento de cargar el componente

**Archivos:**
- `frontend/src/views/Treasury/CashAccountsView.vue`

### 1.2 Errores de Routing en API
**Problema:** La API devolvía errores 400/405 debido a URLs mal configuradas.

**Solución:**
- Removido `process.env.VUE_APP_API_URL` de los stores de treasury y accounting
- Cambiado `baseURL` en `api.js` a "/" para usar routing dinámico vía nginx proxy
- Agregada configuración de proxy en nginx para rutas `/api/`

**Archivos:**
- `frontend/src/services/api.js`
- `frontend/src/store/modules/treasury.js`
- `frontend/src/store/modules/accounting.js`
- `frontend/nginx.conf`

### 1.3 Cuenta Contable 2205 (Proveedores) No Existía
**Problema:** Al crear productos con pago a crédito, el sistema buscaba la cuenta 2205 que no existía en el plan de cuentas.

**Solución:**
- Agregada cuenta 2205 "Proveedores" al plan de cuentas por defecto en `accounting_service.py`
- Creada manualmente la cuenta en la base de datos existente

**Archivos:**
- `backend/app/services/accounting_service.py`

### 1.4 Error 400 al Crear Productos desde Carga Masiva
**Problema:** Al crear productos desde la extracción de facturas PDF, el payment_method no se propagaba correctamente.

**Solución:**
- Modificado `PurchaseFormView.vue` para incluir `payment_method` en el `draftProductData`
- Modificado `ProductForm.vue` para restaurar el `payment_method` desde el draft

**Archivos:**
- `frontend/src/views/Purchases/PurchaseFormView.vue`
- `frontend/src/components/Inventory/ProductForm.vue`

---

## 2. Nuevas Funcionalidades

### 2.1 Vista de Cuentas por Pagar
**Descripción:** Nueva vista para seguimiento de facturas pendientes con alertas de vencimiento.

**Características:**
- Resumen de total pendiente, vencido y próximo a vencer
- Tabla con facturas agrupadas por estado
- Indicadores visuales (rojo = vencido, amarillo = próximo)
- Pestañas para filtrar por estado
- Cálculo automático de días hasta vencimiento

**Backend:**
- Nuevo endpoint `GET /api/v1/purchases/accounts-payable`
- Nuevo método `get_accounts_payable()` en `purchase_service.py`

**Frontend:**
- Nuevo componente `AccountsPayableView.vue`
- Ruta agregada en `router/index.js`
- Enlace en menú lateral (`SidebarNav.vue`)

**Archivos:**
- `backend/app/api/v1/routers/purchases.py`
- `backend/app/services/purchase_service.py`
- `frontend/src/views/Purchases/AccountsPayableView.vue`
- `frontend/src/router/index.js`
- `frontend/src/components/layout/SidebarNav.vue`

### 2.2 Logging en Endpoint de Inventario
**Descripción:** Agregados logs para facilitar debugging de errores en creación de productos.

**Archivos:**
- `backend/app/api/v1/routers/inventory.py`

---

## 3. Scripts de Base de Datos

### 3.1 Script de Reset de Base de Datos
**Descripción:** Script automático para reiniciar la base de datos a estado inicial.

**Funcionalidades:**
- Detiene contenedores
- Elimina volumen de datos (borra todo)
- Recrea servicios
- Ejecuta migraciones automáticamente
- Crea datos iniciales:
  - Usuario admin: `admin@admin.com` / `admin123`
  - Empresa demo: "Mi Empresa"
  - Proveedor demo
  - Plan de cuentas colombiano (48 cuentas)

**Archivos:**
- `reset_database.sh` (script bash)
- `backend/scripts/init_database.py` (script Python)
- `backend/app/scripts/init_database.py` (copia en app)

---

## 4.Mejoras de Contabilidad

### 4.1 Cuenta 2205 - Proveedores
**Descripción:** Agregada la cuenta 2205 "Proveedores" al plan de cuentas estándar colombiano.

**Características:**
- Código: 2205
- Nombre: Proveedores
- Tipo: Pasivo (LIABILITY)
- Descripción: Cuentas por pagar a proveedores

**Archivo:**
- `backend/app/services/accounting_service.py`

---

## 5. Pendientes por Implementar

- [ ] Agregar cuentas bancarias y de caja con saldos iniciales al reset
- [ ] Mejorar mensajes de error en formularios
- [ ] Validación de límite de crédito por proveedor
- [ ] Notificaciones automáticas de facturas por vencer

---

## 6. Comandos Útiles

### Reiniciar base de datos completa:
```bash
cd /home/geralexcas/Reload_Matrix_II
./reset_database.sh
```

### Ver logs del backend:
```bash
docker compose logs --tail=50 backend
```

### Ver logs del frontend:
```bash
docker compose logs --tail=50 frontend
```

### Ver estado de contenedores:
```bash
docker compose ps
```

---

## 7. URLs de Acceso

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:8081 |
| Backend API | http://localhost:8001 |
| PostgreSQL | localhost:5434 |

---

## 8. Credenciales

| Usuario | Email | Password |
|---------|-------|----------|
| Administrador | admin@admin.com | admin123 |

---

*Documento generado el 8 de Mayo de 2026*
*Sistema: Reload Matrix II - Business Management*