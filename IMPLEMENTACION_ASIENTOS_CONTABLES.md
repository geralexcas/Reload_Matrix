# Implementación: Asientos Contables Automáticos - Item 3

**Fecha:** 31 de marzo 2026

## Descripción

Se implementó la creación automática de asientos contables en el libro diario al generar facturas desde reparaciones y facturas generales. Anteriormente, al generar una factura no se creaba automáticamente el asiento contable.

## Cambios realizados

### 1. AccountingService - Nuevos métodos

**Archivo:** `backend/app/services/accounting_service.py`

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

### 2. RepairService - Integración con contabilidad

**Archivo:** `backend/app/services/repair_service.py`

Método `create_invoice_from_repair()` actualizado para:
- Crear automáticamente asiento contable al generar factura desde reparación
- Detectar si es garantía (warranty_applied=True) y crear asiento de costos sin ingreso
- Para facturas normales, crear asiento con ingreso e IVA según régimen

### 3. InvoicingService - Integración con contabilidad

**Archivo:** `backend/app/services/invoicing_service.py`

Nuevo método `_create_automatic_journal_entry()`:
- Calcula subtotal e impuestos desde los items de la factura
- Detecta régimen de la empresa (SIMPLE vs COMUN/ESPECIAL)
- Crea asiento contable automático respetando el régimen tributario

Métodos `create_invoice()` y `create_invoice_with_items()` actualizados para:
- Llamar automáticamente a `_create_automatic_journal_entry()` después de crear la factura
- Los asientos se marcan como `is_posted=True` automáticamente

## Flujo contable automático

### Factura normal (Régimen Común):
```
Debe: Cuentas por cobrar (1130)     $119,000
  Haber: Ingresos por ventas (4100)  $100,000
  Haber: IVA generado (2130)         $19,000
```

### Factura (Régimen Simple):
```
Debe: Cuentas por cobrar (1130)     $100,000
  Haber: Ingresos por ventas (4100)  $100,000
```

### Reparación en garantía:
```
Debe: Costo de ventas (5100)        $50,000
  Haber: Inventarios (1140)          $50,000
```

## Verificación

Todos los imports verifican correctamente:
- AccountingService con nuevos métodos ✅
- InvoicingService con integración contable ✅
- RepairService con asientos automáticos ✅
- Aplicación FastAPI completa ✅
