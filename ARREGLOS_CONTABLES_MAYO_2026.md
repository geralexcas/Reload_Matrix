# Arreglos del Módulo Contable - Mayo 2026

## Resumen de cambios realizados para la aplicación Reload Matrix II

---

## 1. Selector de Cuentas Contables en Cajas (Frontend)

### Problema
Al crear una nueva caja en Treasury → Cajas, el selector de "Cuenta contable vinculada" no mostraba ninguna opción, estaba vacío.

### Causa Raíz
- El componente `CashAccountsView.vue` llamaba a `fetchChartOfAccounts()` sin pasar el `companyId`
- Los stores (`treasury.js`, `accounting.js`) usaban `process.env.VUE_APP_API_URL` que evaluaba como `undefined` en producción
- Esto causaba que las URLs fueran como `http://localhost:8001/undefined/api/v1/...`

### Solución Aplicada
1. **CashAccountsView.vue**: Cambió de usar el getter del store a usar directamente `sessionStorage.getItem('selectedCompanyId')`
2. **Stores (treasury.js, accounting.js)**: Eliminó todas las referencias a `process.env.VUE_APP_API_URL` y cambió a rutas relativas `/api/v1/...`
3. **api.js**: Cambió el baseURL de hardcodeado a `/` (ruta relativa) para funcionar con el proxy de nginx

---

## 2. Asientos Contables Automáticos (Backend)

### Problema
Al crear una empresa, solo se creaba el plan de cuentas pero no se generaban los asientos contables requeridos por la legislación colombiana.

### Solución Aplicada

#### 2.1 Asiento de Apertura (`accounting_service.py`)
- Nuevo método `create_opening_entry()` que crea el asiento de apertura inicial
- Registra: efectivo, bancos, capital social
- Cumple con el Decreto 2420/2015 de normativa colombiana

#### 2.2 Asientos para Cajas (`treasury_service.py`)
- Método `create_cash_account()` ahora genera automáticamente el asiento contable cuando se crea una caja con saldo inicial
- Usa cuenta de capital (3100) como contraparte

#### 2.3 Asientos para Bancos (`treasury_service.py`)
- Método `create_bank_account()` mejorado para usar cuenta de capital (3100) como contraparte en lugar de la misma cuenta
- Genera asientos automáticos con saldo inicial

#### 2.4 Depósitos y Retiros (`treasury_service.py`)
- Corregido el bug en depósitos a cajas que usaba la misma cuenta en ambos lados del asiento
- Ahora usa cuenta de capital (3100) como contraparte

---

## 3. Configuración del Proxy Nginx

### Problema
El login fallaba con error 405 (Not Allowed) luego 502 (Bad Gateway) porque el nginx no tenía configurado el proxy para las rutas del API.

### Solución Aplicada
- Editado `frontend/nginx.conf` para agregar proxy inverso:
  ```nginx
  location /api/ {
      proxy_pass http://backend:8000/api/;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
  }
  ```

---

## Archivos Modificados

### Frontend
- `frontend/src/views/Treasury/CashAccountsView.vue` - Carga de companyId
- `frontend/src/services/api.js` - BaseURL dinámico
- `frontend/src/store/modules/treasury.js` - Rutas relativas
- `frontend/src/store/modules/accounting.js` - Rutas relativas
- `frontend/nginx.conf` - Proxy para API

### Backend
- `backend/app/services/accounting_service.py` - Método create_opening_entry()
- `backend/app/services/treasury_service.py` - Asientos automáticos para cajas y bancos

---

## Estado Final
- ✅ Selector de cuentas contables funcionando
- ✅ Login funcionando a través del proxy nginx
- ✅ Asientos contables automáticos creados para cajas y bancos
- ✅ Sistema de producción funcionando correctamente

---

*Documento generado: Mayo 2026*
*Aplicación: Reload Matrix II*