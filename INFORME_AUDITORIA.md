# Informe de Auditoría Contable — Reload Matrix

**Fecha:** 22/06/2026  
**Alcance:** Módulos de Asientos Contables, Facturación e Inventario  
**Metodología:** Revisión estática de código fuente, escritorio de pruebas y ejecución de suite `test_contabilidad.py`

---

## Resultado de Tests

| Suite | Resultado |
|-------|-----------|
| `TestPartidaDoble` (3 tests) | PASSED |
| `TestInventarioNoNegativo` (3 tests) | PASSED |
| `TestFacturacionAtomicidad` (1 test) | PASSED |
| `TestReportesFinancieros` (1 test) | PASSED |

> Los 8 tests pasan pero **no cubren los bugs críticos** detectados en la auditoría profunda del código fuente.

---

## 1. MÓDULO DE ASIENTOS CONTABLES (Partida Doble)

### C1 — CRÍTICO: Sin validación de periodos cerrados
- **Archivo:** `app/services/accounting_service.py:255-422` (`post_journal_entry`)
- **Problema:** No existe modelo de periodo fiscal ni validación de fecha. Se puede contabilizar en cualquier periodo histórico, violando el Decreto 2420/2015 colombiano.
- **Solución:** Crear modelo `FiscalPeriod` con `start_date`, `end_date`, `is_closed`. Validar en `post_journal_entry` que `entry_date` caiga dentro de un periodo abierto.

### C2 — CRÍTICO: Race condition en posteo sin `SELECT FOR UPDATE`
- **Archivo:** `app/services/accounting_service.py:257`
- **Problema:** `not db_je.is_posted` se lee sin lock. Dos requests concurrentes pueden postear el mismo asiento, actualizando balances bancarios doble vez.
- **Solución:** Usar `with_for_update()` en la query del journal entry al postear.

### C3 — CRÍTICO: Actualización no-atómica de balances bancarios
- **Archivo:** `app/services/accounting_service.py:327, 381`
- **Problema:** `bank_acct.current_balance += net_change` es una operación Python-level, no un `UPDATE SET current_balance = current_balance + :val` SQL atómico. Bajo concurrencia se pierden actualizaciones (lost update).
- **Solución:** Usar query atómica: `self.db.query(BankAccount).filter(BankAccount.id == bank_acct.id).update({BankAccount.current_balance: BankAccount.current_balance + net_change})`.

### C4 — CRÍTICO: Fuzzy prefix matching corrompe balances de tesorería
- **Archivo:** `app/services/accounting_service.py:302-323, 356-377`
- **Problema:** Si no hay match exacto de `linked_account_id`, hace `line_code.startswith(c_code) or c_code.startswith(line_code)`. Una cuenta "11" haría match con "1110", "1120", etc., actualizando saldos bancarios incorrectos.
- **Solución:** Eliminar el fallback fuzzy. Solo sincronizar tesorería cuando haya `linked_account_id` exacto.

### M1 — MEDIO: `reverse_journal_entry` no verifica si el original está posteado
- **Archivo:** `app/services/accounting_service.py:167-205`
- **Problema:** Revierte asientos no posteados (sin sentido contable) y pone `is_posted=True` al reversal sin pasar por `post_journal_entry`, bypasseando la sincronización con tesorería.
- **Solución:** Verificar `original.is_posted == True` antes de revertir. Llamar `post_journal_entry` para el reversal o duplicar la sincronización de tesorería.

### M2 — MEDIO: Inconsistencia en filtros de fecha entre reportes
- **Archivo:** `app/services/accounting_service.py:737` (libro ventas) vs `448` (balance prueba)
- **Problema:** `libro_ventas` no aplica end-of-day en `date_to`. `libro_compras` usa `sql_func.date()` que depende de timezone de sesión.
- **Solución:** Unificar usando `datetime.combine(date_to, time(23,59,59))` en todos los reportes.

### L1 — MENOR: `float(uvt_daily_threshold)` pierde precisión Decimal
- **Archivo:** `app/services/accounting_service.py:1318`
- **Solución:** Mantener como `Decimal` en el response schema.

### L2 — MENOR: Debug `print()` en producción
- **Archivo:** `app/api/v1/routers/accounting.py:600`
- **Solución:** Eliminar o reemplazar con `logger.debug()`.

---

## 2. MÓDULO DE FACTURACIÓN (Trazabilidad en Cascada)

### F1 — CRÍTICO: Doble conteo de IVA en asiento automático
- **Archivo:** `app/services/invoicing_service.py:126, 136`
- **Problema:** `subtotal += item.line_total` donde `line_total` YA incluye IVA. Luego `total_amount = subtotal + tax_amount` suma el IVA dos veces. El débito a Cuentas por Cobrar será mayor al real.
- **Solución:** Calcular `subtotal = sum(item.line_total - item.tax_amount for item in items)`, luego `total_amount = subtotal + tax_amount`.

### F2 — CRÍTICO: `POST /` (create_invoice simple) no descuenta inventario
- **Archivo:** `app/services/invoicing_service.py:164-209`
- **Problema:** Crea factura sin items ni deducción de inventario, PERO genera asiento contable. Inconsistencia: registros contables sin movimiento de stock.
- **Solución:** Eliminar el endpoint simple o redirigir a `create_invoice_with_items`. Como mínimo, no generar asiento contable si no hay items.

### F3 — ALTO: `update_invoice` permite modificar cualquier campo sin validación
- **Archivo:** `app/services/invoicing_service.py:462-485`
- **Problema:** Se puede cambiar `status` de PAID a DRAFT, o `total_amount` después de creado el asiento contable, sin recalcular.
- **Solución:** Crear schema `InvoiceUpdate` con campos restringidos. Bloquear modificación de facturas con asientos contables ya generados.

### F4 — MEDIO: DELETE endpoint siempre devuelve 500
- **Archivo:** `app/api/v1/routers/invoicing.py:129-148`
- **Problema:** `delete_invoice()` siempre lanza `ValueError` pero el router no lo captura → HTTP 500.
- **Solución:** Retornar `405 Method Not Allowed` o capturar ValueError como 400.

### F5 — MEDIO: Heurística frágil "INV-17" para timestamps
- **Archivo:** `app/services/invoicing_service.py:180`
- **Problema:** Reemplaza silenciosamente números de factura que empiezan con "INV-17" asumiendo que son timestamps JS. Romperá ~2286 y puede sobreescribir números legítimos.
- **Solución:** Eliminar esta heurística. Delegar al backend la generación de número.

### F6 — MEDIO: Reversión de wallet usa LIKE frágil
- **Archivo:** `app/services/invoicing_service.py:558`
- **Problema:** `description.like(f"%{invoice_number}%")` puede matchear transacciones no relacionadas.
- **Solución:** Agregar `invoice_id` como FK en `WalletTransaction` para referencia directa.

### F7 — MEDIO: Cancelación no revierte RepairOrder
- **Archivo:** `app/services/invoicing_service.py:261-265` (set) vs cancel (no revierte)
- **Problema:** Al crear factura se setea `repair_order.status = "DELIVERED"`, pero al cancelar no se revierte.
- **Solución:** En `cancel_invoice`, si hay repair_order vinculado, revertir `invoice_id` y el status al anterior.

---

## 3. MÓDULO DE INVENTARIOS (Kárdex)

### I1 — CRÍTICO: `update_product` permite sobreescribir `stock_level` directamente
- **Archivo:** `app/services/inventory_service.py:276`
- **Problema:** `setattr` con `model_dump()` permite `PUT` con `stock_level: 9999`, bypasseando `add_stock`/`deduct_stock` sin rastro.
- **Solución:** Crear `ProductUpdate` schema con `stock_level` y `purchase_price` excluidos. Manejar stock solo via endpoints dedicados.

### I2 — ALTO: `add_stock` sin `with_for_update()` → lost updates
- **Archivo:** `app/services/inventory_service.py:376`
- **Problema:** Lee stock sin lock y hace `+= ` en Python. Dos receipts concurrentes para el mismo producto → una actualización se pierde.
- **Solución:** Agregar `with_for_update()` como en `deduct_stock` y `adjust_stock_level`.

### I3 — ALTO: No existe Kárdex (movimientos de inventario)
- **Problema:** No hay modelo `InventoryMovement` ni tabla de kárdex. Los parámetros `reference/reference_id/reference_type` en `add_stock` se reciben pero NUNCA se persisten. Incumple el Art. 63 del Código de Comercio y requisitos DIAN.
- **Solución:** Crear modelo `InventoryMovement` con `product_id`, `movement_type`, `quantity`, `unit_cost`, `reference`, `reference_id`, `balance_after`. Registrar movimientos en todos los métodos de stock.

### I4 — ALTO: Método de costeo no cumple NIIF/NIC 2
- **Archivo:** `app/services/invoicing_service.py:131`
- **Problema:** Usa `product.purchase_price` (último precio de compra) como costo de venta. No es FIFO ni ponderado. Al comprar a distinto precio, no hay capas de costo.
- **Solución:** Implementar Promedio Ponderado: mantener `weighted_average_cost` en el modelo Producto, recalcular en cada compra con fórmula: `(costo_actual × stock_actual + costo_nuevo × cant_nueva) / (stock_actual + cant_nueva)`.

### I5 — ALTO: Constraints `unique` de SKU/barcode son globales, no por empresa
- **Archivo:** `app/models/sql/inventory.py:12, 15`
- **Problema:** Dos empresas no pueden tener el mismo SKU o barcode. Rompe aislamiento multi-tenant.
- **Solución:** Cambiar a `UniqueConstraint('sku', 'company_id')` y `UniqueConstraint('barcode', 'company_id')` como constraints compuestos.

### I6 — MEDIO: Parámetros `quantity: float` en vez de `Decimal`
- **Archivo:** `app/services/inventory_service.py:318, 368`, router `inventory.py:310`
- **Problema:** `float` pierde precisión (ej: `0.1` no es exactamente `0.1` en binario).
- **Solución:** Cambiar tipo a `Decimal` en service y router.

### I7 — MEDIO: Conflicto de rutas para barcodes numéricos
- **Archivo:** `app/api/v1/routers/inventory.py:145` vs `228`
- **Problema:** Un barcode EAN puramente numérico (ej: "7701234567890") matchea primero `/{product_id}` como int.
- **Solución:** Registrar `/barcode/` y `/low-stock/` ANTES de `/{product_id}`.

---

## 4. VULNERABILIDADES DE SEGURIDAD TRANSVERSALES

### S1 — CRÍTICO: Sin verificación de pertenencia a empresa (cross-tenant)
- **Archivos:** Todos los routers de accounting, invoicing, inventory
- **Problema:** `company_id` es un query parameter. Cualquier usuario autenticado puede acceder a datos de cualquier empresa pasando un `company_id` arbitrario. No se usa `verify_company_membership()` ni `require_permission()`.
- **Solución:** Agregar `Depends(verify_company_membership)` y `Depends(require_permission(...))` en todos los endpoints.

### S2 — MEDIO: `model_dump()` pasa campos del cliente directamente al ORM
- **Archivos:** `app/services/invoicing_service.py:196`, `app/services/inventory_service.py:276`
- **Problema:** `Invoice(**invoice_data)` sin allowlist. Un cliente puede enviar `status="PAID"` al crear, bypasseando el flujo de pago.
- **Solución:** Usar allowlists explícitos o schemas de Create separados sin campos de estado.

---

## 5. RESUMEN POR SEVERIDAD

| Severidad | Cantidad | IDs |
|-----------|----------|-----|
| **CRÍTICO** | 7 | C1, C2, C3, C4, F1, F2, I1, S1 |
| **ALTO** | 5 | M1, F3, I2, I3, I4, I5 |
| **MEDIO** | 8 | M2, F4, F5, F6, F7, I6, I7, S2 |
| **MENOR** | 2 | L1, L2 |

## 6. PRIORIDAD DE CORRECCIÓN

1. **F1** — Doble conteo de IVA (descuadre financiero real)
2. **C4** — Fuzzy prefix matching (corrupción de saldos bancarios)
3. **S1** — Sin verificación multi-tenant (exposición de datos)
4. **C2+C3** — Race condition + actualización no-atómica en posteo
5. **I1** — Bypass de control de stock via PUT
6. **I3** — Sin Kárdex (incumplimiento regulatorio)
7. **I4** — Método de costeo no cumple NIIF
8. **C1** — Sin periodos cerrados
