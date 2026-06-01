# Plan de Corrección - Módulo de Contabilidad (Cuentas por defecto e Idempotencia)

**Fecha:** 2026-06-01

## Problemas Identificados

### 1. Cuenta 2408 (IVA soportado) FALTANTE — Error 400 al crear productos
- **Síntoma:** `Required chart of accounts not found for purchases` al crear producto con proveedor
- **Causa raíz:** `create_journal_entry_from_purchase` (`accounting_service.py:2634`) busca la cuenta `2408` (IVA soportado) pero no existe en el plan de cuentas por defecto (`create_default_chart_of_accounts`, línea 1617)
- **Impacto COMUN/ESPECIAL:** El IVA soportado nunca se registra contablemente (se omite silenciosamente por `and tax_receivable`)
- **Impacto SIMPLE:** No usa la cuenta 2408 (correcto por normativa), pero al no existir, no causa error directo

### 2. Cuenta 6135 (Costo de ventas detallado) FALTANTE
- **Causa raíz:** `create_journal_entry_from_invoice` (`accounting_service.py:2292`) busca `6135` para registrar COGS al facturar con `total_cost > 0`
- **Impacto:** El costo de ventas detallado no se registra al facturar. La cuenta `5100` sí existe y se usa en garantías/inventario, pero la facturación busca `6135`

### 3. `create_default_chart_of_accounts` NO es idempotente — UniqueViolation
- **Síntoma:** `duplicate key value violates unique constraint "uq_chart_code_company"` al ejecutar más de una vez
- **Causa raíz:** No verifica si las cuentas ya existen antes de crearlas
- **Impacto:** `init_database.py` falla si se re-ejecuta; no se pueden agregar cuentas faltantes a empresas existentes

### 4. Enum `account_types` no incluye "COST"
- **Causa raíz:** El modelo `ChartOfAccounts` define el enum como `"ASSET", "LIABILITY", "EQUITY", "REVENUE", "EXPENSE"` pero `_get_account_balance_by_type` (línea 2548) y `get_estado_resultados` (línea 2459) buscan tipo `"COST"`
- **Impacto:** Los reportes de estado de resultados nunca calculan costos correctamente (siempre retornan vacío)

### 5. Warning SQLAlchemy en ChartOfAccounts
- **Síntoma:** `relationship 'ChartOfAccounts.children' will copy column... conflicts with relationship(s): 'ChartOfAccounts.parent'`
- **Causa raíz:** Relación `children` no tiene `overlaps="parent"`

### 6. Inconsistencia código 5100 vs 6135
- Garantías/inventario usan `5100` (Costo de ventas genérico)
- Facturación usa `6135` (Costo de ventas detallado PUC)
- Ambas son válidas según PUC colombiano, pero deben existir ambas

## Análisis: Régimen Simple

El código **ya maneja correctamente** la lógica de régimen Simple en compras:

```python
# create_journal_entry_from_purchase (línea 2631)
is_simple_regime = company.regimen in ("SIMPLE", "NO_RESPONSABLE")

# IVA soportado solo para no-Simple (línea 2668)
if not is_simple_regime and tax_amount > 0 and tax_receivable:
    # Registra IVA soportado

# Para Simple, todo va a Inventarios incluyendo el IVA (línea 2661)
debit_amount=subtotal if not is_simple_regime else total_amount
```

**Decisión:** La cuenta 2408 debe existir en el plan para todas las empresas, pero se puede desactivar (`is_active=False`) para Simple/No Responsable. Así:
- COMUN/ESPECIAL: usa 2408 normalmente
- SIMPLE: la cuenta existe pero no se usa ni aparece en el plan activo
- Si empresa cambia de régimen, se puede reactivar

## Análisis: Empresas Nuevas

El flujo actual en `company.py:78-79`:
```python
accounting_svc = accounting_service.AccountingService(db)
accounting_svc.create_default_chart_of_accounts(db_company.id)
```

- Cada empresa nueva **sí** obtiene el plan de cuentas al crearse
- Pero el plan está **incompleto** (faltan 2408, 6135)
- Al corregir e implementar idempotencia, empresas nuevas tendrán todas las cuentas
- Empresas existentes pueden ejecutar `create_default_chart_of_accounts(company_id)` para llenar las faltantes sin error

## Cuentas Contables: Buscadas vs Existentes

### Cuentas FALTANTES (no están en default_accounts pero el código las busca)

| Código | Nombre | Tipo | Quien la busca | Criticidad |
|--------|--------|------|----------------|------------|
| 2408 | IVA soportado | LIABILITY | `create_journal_entry_from_purchase` | CRÍTICA |
| 6135 | Costo de ventas | EXPENSE | `create_journal_entry_from_invoice` (COGS) | ALTA |

### Cuentas EXISTENTES (OK)

| Código | Usado en |
|--------|----------|
| 1110 | create_opening_entry |
| 111001 | create_opening_entry, invoices, purchases, initial_stock |
| 111010 | create_opening_entry, invoices, purchases, initial_stock |
| 1130 | create_journal_entry_from_invoice |
| 1140 | invoices, purchases, initial_stock, warranty |
| 2205 | create_journal_entry_from_purchase, initial_stock |
| 2130 | create_journal_entry_from_invoice (IVA generado) |
| 2150 | wallet_service, create_journal_entry_from_invoice (anticipos) |
| 4100 | create_journal_entry_from_invoice (ventas) |
| 5100 | warranty, inventory journal entries |
| 3100 | create_opening_entry, treasury_service |
| 5400 | treasury_service (gastos financieros) |
| 4200 | treasury_service (intereses) |
| 2110 | treasury_service (cuentas por pagar) |

## Plan de Implementación

### Paso 1: Agregar cuentas faltantes al `default_accounts`
- Archivo: `backend/app/services/accounting_service.py`
- Agregar cuenta `2408` (IVA soportado, LIABILITY) en sección de pasivos
- Agregar cuenta `6135` (Costo de ventas, EXPENSE) en sección de gastos

### Paso 2: Hacer idempotente `create_default_chart_of_accounts`
- Archivo: `backend/app/services/accounting_service.py`
- Antes de crear cada cuenta, verificar si ya existe por `(code, company_id)`
- Si existe, usar la existente en lugar de crear nueva
- Retornar todas las cuentas (existentes + nuevas)

### Paso 3: Desactivar cuenta 2408 para empresas Simple
- En `create_default_chart_of_accounts`, después de crear las cuentas, verificar el régimen de la empresa
- Si es SIMPLE o NO_RESPONSABLE, poner `is_active=False` en la cuenta 2408

### Paso 4: Corregir warning SQLAlchemy en ChartOfAccounts
- Archivo: `backend/app/models/sql/accounting/chart_of_accounts.py`
- Agregar `overlaps="parent"` a la relación `children`

### Paso 5: Manejar tipo COST en el enum
- Opción elegida: Agregar "COST" al enum `account_types` + generar migración Alembic
- Actualizar `_get_account_balance_by_type` (ya lo busca correctamente)
- Cambiar `5100` y `6135` de tipo EXPENSE a COST (son cuentas de costo, no de gasto)

### Paso 6: Escribir tests unitarios
- Archivo: `backend/tests/unit/test_accounting_service.py`
- Tests:
  1. `create_default_chart_of_accounts` es idempotente (se puede llamar 2 veces sin error)
  2. `create_default_chart_of_accounts` crea todas las cuentas requeridas
  3. `_get_account_by_code` encuentra todas las cuentas después de crear el plan
  4. `create_journal_entry_from_purchase` funciona con plan completo (COMUN)
  5. `create_journal_entry_from_purchase` funciona con plan completo (SIMPLE, no usa 2408)
  6. Cuenta 2408 se desactiva para empresas SIMPLE

### Paso 7: Verificar con linter y tests existentes
- `ruff check app/`
- `pytest --cov=app --cov-report=term-missing`

## Migración para Servidores Existentes

Después de deployar, ejecutar en cada servidor:
```bash
docker compose exec backend python -c "
from app.core.database import SessionLocal
from app.services.accounting_service import AccountingService
from app.models.sql.company import Company

db = SessionLocal()
companies = db.query(Company).all()
for company in companies:
    svc = AccountingService(db)
    accounts = svc.create_default_chart_of_accounts(company.id)
    db.commit()
    print(f'Empresa {company.id} ({company.name}): {len(accounts)} cuentas verificadas')
db.close()
"
```

Esto creará solo las cuentas faltantes (2408, 6135) sin duplicar las existentes, gracias a la idempotencia.
