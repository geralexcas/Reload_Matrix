# Módulo de Compras - Implementado

## Descripción General

Módulo implementado para gestionar las facturas emitidas por proveedores, incluyendo:
- ✅ Registro de facturas de compra
- ✅ Control de formas de pago (contado, crédito, transferencia bancaria, etc.)
- ✅ Actualización automática del inventario
- ✅ Integración con el módulo contable

## Archivos Creados/Modificados

### Backend

1. **Modelos de Datos** - `app/models/sql/purchases.py` ✅ CREADO
   - Modelo `Purchase`: Factura de compra
   - Modelo `PurchaseItem`: Items de la factura  
   - Modelo `PurchasePayment`: Pagos registrados

2. **Esquemas Pydantic** - `app/schemas/purchase.py` ✅ CREADO
   - `PurchaseCreate`, `PurchaseUpdate`, `PurchaseResponse`
   - `PurchaseItemCreate`, `PurchaseItemResponse`
   - `PurchasePaymentCreate`, `PurchasePaymentResponse`
   - `PurchaseStatistics`

3. **Servicio de Negocio** - `app/services/purchase_service.py` ✅ CREADO
   - `create_purchase()`: Crear factura de compra
   - `update_inventory_from_purchase()`: Actualizar inventario
   - `create_accounting_entry()`: Generar asiento contable
   - `register_payment()`: Registrar pago
   - `get_statistics()`: Obtener estadísticas

4. **Rutas API** - `app/api/v1/routers/purchases.py` ✅ CREADO
   - `POST /purchases/`: Crear factura
   - `GET /purchases/`: Listar facturas
   - `GET /purchases/{id}`: Ver detalle
   - `PUT /purchases/{id}`: Actualizar
   - `DELETE /purchases/{id}`: Eliminar
   - `POST /purchases/{id}/pay`: Registrar pago
   - `GET /purchases/statistics`: Estadísticas

### Archivos Actualizados

- ✅ `app/models/sql/__init__.py` - Exportar modelos de compras
- ✅ `app/schemas/__init__.py` - Exportar esquemas de compras
- ✅ `app/services/__init__.py` - Exportar servicio de compras
- ✅ `app/api/v1/routers/__init__.py` - Registrar router de compras

### Migración de Base de Datos

- ✅ `alembic/versions/XXXX_add_purchases_module.py` - Tablas de compras

## Campos del Modelo Purchase

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | ID único |
| purchase_number | String | Número de factura del proveedor |
| partner_id | Integer | FK al proveedor |
| purchase_date | DateTime | Fecha de emisión |
| due_date | DateTime | Fecha de vencimiento |
| subtotal | Numeric | Subtotal sin impuestos |
| tax_amount | Numeric | Monto de impuestos |
| total_amount | Numeric | Total con impuestos |
| currency | String | Moneda (COP, USD) |
| payment_method | Enum | Forma de pago |
| status | Enum | Estado de la factura |
| company_id | Integer | FK a empresa |
| created_at | DateTime | Fecha de creación |
| updated_at | DateTime | Fecha de actualización |

## Formas de Pago Soportadas

- `CASH` - Efectivo
- `BANK_TRANSFER` - Transferencia bancaria
- `CHECK` - Cheque
- `CREDIT_CARD` - Tarjeta de crédito
- `CREDIT` - Crédito directo con proveedor
- `PARTIAL_CREDIT` - Crédito parcial

## Estados de Factura

- `DRAFT` - Borrador
- `ISSUED` - Emitida
- `PAID` - Pagada
- `PARTIAL` - Pagada parcialmente
- `OVERDUE` - Vencida
- `CANCELLED` - Anulada

## Integraciones

### 1. Inventario
- Al crear una factura de compra con productos:
  - Se aumentan las existencias del producto
  - Se actualiza el precio de compra

### 2. Contabilidad
- Se crea automáticamente un asiento contable:
  - **Débit**: Cuenta de inventario/gastos (1.5.x.x)
  - **Crédito**: Cuenta por pagar a proveedor (2.1.x.x)
  - O según la forma de pago (banco, caja)

### 3. Tesorería
- Al registrar pago:
  - Se crea transacción en tesorería
  - Se actualiza saldo de banco/caja

## Ejemplo de Uso

### Crear una factura de compra

```json
POST /api/v1/purchases/?company_id=1
{
  "purchase_number": "FVE-001234",
  "partner_id": 5,
  "purchase_date": "2026-04-03T10:00:00",
  "due_date": "2026-05-03T10:00:00",
  "payment_method": "CREDIT",
  "items": [
    {
      "product_id": 1,
      "description": "Producto A",
      "quantity": 10,
      "unit_price": 10000,
      "tax_rate": 19,
      "line_total": 119000
    }
  ]
}
```

### Registrar un pago

```json
POST /api/v1/purchases/1/pay
{
  "payment_method": "BANK_TRANSFER",
  "amount": 119000,
  "payment_date": "2026-04-03T15:00:00",
  "reference": "TRF-12345"
}
```

## Consideraciones

1. **Validación de inventario**: Solo se actualiza si el item tiene `product_id`
2. **Asiento contable**: Se genera automáticamente al crear la factura
3. **Pagos parciales**: Soporta pagos parciales con seguimiento de saldo
4. **Régimen tributario**: Calcula impuestos según el régimen de la empresa (SIMPLE vs COMUN)