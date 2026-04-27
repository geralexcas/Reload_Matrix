# Implementación: Descuento de Inventario en Reparaciones - Item 4

**Fecha:** 31 de marzo 2026

## Descripción

Se implementó el descuento automático de inventario cuando se usan repuestos en reparaciones. Al generar la factura desde una orden de reparación, los productos vinculados a los repair_items se descuentan automáticamente del stock.

## Cambios realizados

### 1. InventoryService - Nuevos métodos

**Archivo:** `backend/app/services/inventory_service.py`

#### `deduct_stock(product_id, quantity, company_id)`
- Descuenta stock de un producto
- Valida que el producto exista
- Valida stock suficiente (lanza error si no hay suficiente)
- Actualiza y retorna el producto con el nuevo stock

#### `check_stock_availability(product_id, quantity, company_id)`
- Verifica si hay stock suficiente sin modificar
- Retorna booleano

### 2. RepairService - Integración con inventario

**Archivo:** `backend/app/services/repair_service.py`

Método `create_invoice_from_repair()` actualizado para:
- Recorrer todos los repair_items que tienen `product_id` vinculado
- Descontar automáticamente del inventario usando `InventoryService.deduct_stock()`
- Registrar los productos descontados con cantidad y stock restante
- Si no hay stock suficiente, la factura NO se genera (error)

### 3. InvoicingService - Descuento en facturas generales

**Archivo:** `backend/app/services/invoicing_service.py`

Método `create_invoice_with_items()` actualizado para:
- Descontar inventario de los items de factura que tienen `product_id`
- Se ejecuta antes de crear el asiento contable

### 4. Nuevos endpoints de inventario

**Archivo:** `backend/app/api/v1/routers/inventory.py`

#### `POST /api/v1/inventory/{product_id}/deduct-stock`
- Descuento manual de stock (parámetro: quantity)
- Útil para ajustes manuales o consumo directo

#### `GET /api/v1/inventory/{product_id}/check-stock`
- Verificar disponibilidad de stock
- Retorna: `{"available": bool, "current_stock": number, "requested": number, "product_name": str}`

## Flujo automático

### Al generar factura desde reparación:
1. Se valida que la orden esté READY o DELIVERED
2. Se crea la factura con los items de reparación
3. **Por cada repair_item con product_id:** se descuenta del inventario
4. Se crea el asiento contable automático
5. Se vincula la factura a la orden de reparación

### Validaciones:
- Si no hay stock suficiente → Error 400, no se genera factura
- Items sin product_id → No descuentan (son servicios/mano de obra)
- Garantías → También descuentan inventario (se registran costos)

## Verificación

Todos los imports verifican correctamente:
- InventoryService con nuevos métodos ✅
- RepairService con descuento de inventario ✅
- InvoicingService con descuento de inventario ✅
- Router de inventario con nuevos endpoints ✅
- Aplicación FastAPI completa ✅
