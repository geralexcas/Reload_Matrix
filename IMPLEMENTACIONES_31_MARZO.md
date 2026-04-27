# Implementaciones Recientes - 31 Marzo 2026

## Item 3: Asientos Contables Automáticos

### Descripción
Se implementó la creación automática de asientos contables en el libro diario al generar facturas desde reparaciones y facturas generales. Anteriormente, al generar una factura no se creaba automáticamente el asiento contable.

### Archivos modificados
- `backend/app/services/accounting_service.py`
- `backend/app/services/repair_service.py`
- `backend/app/services/invoicing_service.py`

### Nuevos métodos en AccountingService

#### `create_journal_entry_from_invoice()`
Crea asiento contable automático desde una factura, considerando el régimen tributario:

**Régimen Común/Especial:**
- Debe: Cuentas por cobrar (1130) → Total
- Haber: Ingresos por ventas (4100) → Subtotal
- Haber: Obligaciones fiscales/IVA (2130) → Impuesto

**Régimen Simple:**
- Debe: Cuentas por cobrar (1130) → Total
- Haber: Ingresos por ventas (4100) → Total (sin discriminación de IVA)

#### `_create_warranty_journal_entry()`
Crea asiento contable para reparaciones en garantía (sin reconocimiento de ingreso):
- Debe: Costo de ventas (5100) → Costo repuestos
- Haber: Inventarios (1140) → Costo repuestos

#### `create_inventory_journal_entry()`
Crea asiento contable cuando se usa inventario en reparaciones:
- Debe: Costo de ventas (5100) → Costo total
- Haber: Inventarios (1140) → Costo total

### Integración
- `RepairService.create_invoice_from_repair()` → Crea asiento contable automático
- `InvoicingService.create_invoice()` → Crea asiento contable automático
- `InvoicingService.create_invoice_with_items()` → Crea asiento contable automático

---

## Item 4: Descuento de Inventario en Reparaciones

### Descripción
Se implementó el descuento automático de inventario cuando se usan repuestos en reparaciones. Al generar la factura desde una orden de reparación, los productos vinculados a los repair_items se descuentan automáticamente del stock.

### Archivos modificados
- `backend/app/services/inventory_service.py`
- `backend/app/services/repair_service.py`
- `backend/app/services/invoicing_service.py`
- `backend/app/api/v1/routers/inventory.py`

### Nuevos métodos en InventoryService

#### `deduct_stock(product_id, quantity, company_id)`
- Descuenta stock de un producto
- Valida que el producto exista
- Valida stock suficiente (lanza error si no hay suficiente)
- Actualiza y retorna el producto con el nuevo stock

#### `check_stock_availability(product_id, quantity, company_id)`
- Verifica si hay stock suficiente sin modificar
- Retorna booleano

### Nuevos endpoints

#### `POST /api/v1/inventory/{product_id}/deduct-stock`
Descuento manual de stock. Parámetro: `quantity`. Útil para ajustes manuales o consumo directo.

#### `GET /api/v1/inventory/{product_id}/check-stock`
Verificar disponibilidad de stock. Parámetro: `quantity`.
Retorna:
```json
{
  "available": true,
  "current_stock": 50,
  "requested": 5,
  "product_name": "Repuesto XYZ"
}
```

### Integración
- `RepairService.create_invoice_from_repair()` → Descuenta inventario de repair_items con product_id
- `InvoicingService.create_invoice_with_items()` → Descuenta inventario de invoice items con product_id

### Flujo automático
1. Se valida que la orden esté READY o DELIVERED
2. Se crea la factura con los items de reparación
3. **Por cada repair_item con product_id:** se descuenta del inventario
4. Se crea el asiento contable automático
5. Se vincula la factura a la orden de reparación

### Validaciones
- Si no hay stock suficiente → Error 400, no se genera factura
- Items sin product_id → No descuentan (son servicios/mano de obra)
- Garantías → También descuentan inventario (se registran costos)

---

## Verificación General

Todos los imports verifican correctamente:
- AccountingService con nuevos métodos ✅
- InvoicingService con integración contable e inventario ✅
- RepairService con asientos automáticos y descuento de inventario ✅
- InventoryService con descuento y verificación ✅
- Router de inventario con nuevos endpoints ✅
- Aplicación FastAPI completa ✅
