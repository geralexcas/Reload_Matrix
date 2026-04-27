# Flujo de Facturación tipo POS

El objetivo es cambiar el flujo "directo" de creación de facturas (tanto desde el formulario principal de Facturación como desde el botón "Generar Factura" en el módulo de Reparaciones), introduciendo una interfaz tipo Punto de Venta (POS) que permita definir el método de pago e interactuar con el cobro inmediatamente.

## User Review Required

> [!IMPORTANT]
> Este plan afectará el flujo actual de facturación. ¿Estás de acuerdo en que todas las facturas nuevas (desde Reparación y desde Nueva Factura) muestren primero este modal de pago/POS antes de confirmarlas?

## Proposed Changes

### Interfaz General (Componente Reutilizable)

#### [NEW] `frontend/src/components/POSPaymentModal.vue`
Crearemos un nuevo componente modal reutilizable (tipo POS) que se encargará de:
1. Mostrar el total a cobrar.
2. Permitir seleccionar un método de pago (Efectivo, Tarjeta, Transferencia, Crédito, etc.).
3. Si es "Efectivo", habilitar campos para ingresar el "Monto Recibido" y calcular automáticamente el "Cambio" (`Monto Recibido` - `Total`).
4. Si es "Transferencia", solicitar número de referencia (opcional).

### Módulo de Reparación

#### [MODIFY] `frontend/src/views/Repair/RepairDetailView.vue`
- Modificar la acción del botón "Generar Factura" para que, en lugar de invocar la generación en background directamente, abra el `POSPaymentModal.vue` pasándole el objeto `order` y su `calculatedTotal`.
- Al confirmar el pago en el modal POS, se enviará la solicitud al backend (`/generate-invoice/`). En la payload se anexarán los detalles del pago (método, monto pagado).

#### [MODIFY] `backend/app/api/v1/routers/repair.py` & `backend/app/services/repair_service.py`
- Ajustar el endpoint y el servicio de `generate_invoice_from_repair` para que acepte información de pago (payment_method, amount_paid, account_type, account_id).
- Si el usuario suministra la información de pago en el POS, el backend debe:
  1. Crear la factura y los ítems.
  2. Emitirla automáticamente (estado emitido/pagado).
  3. Descontar stock.
  4. Generar la entrada contable y de tesorería (ingreso en caja/banco).

### Módulo de Facturación Central

#### [MODIFY] `frontend/src/views/Invoicing/InvoicingView.vue`
- En lugar de enviar la factura directamente al hacer clic en "Crear Factura", el formulario abrirá el `POSPaymentModal.vue`.
- Una vez el usuario configure cómo le están pagando (efectivo, etc.), se enviará el payload completo a `/api/v1/invoicing/`, incluyendo la data para marcar `is_paid = true`, método de pago, el tipo de cuenta (`CASH` o `BANK`) y el ID de cuenta, tal como lo soporta actualmente el `invoicing_service`.

#### [MODIFY] `frontend/src/store/modules/treasury.js`
- Verificar que el store tenga la capacidad de traer las "Cuentas de Caja" y "Cuentas Bancarias" para poblar los selects en el modal POS (necesario para decirle al backend a dónde va el dinero).

## Open Questions

> [!WARNING]
> ¿Tienes parametrizadas y creadas las cuentas de "Caja" o "Banco" en tu módulo de Tesorería? El backend requiere saber este dato (`payment_account_id` y `payment_account_type`) para inyectar automáticamente el ingreso del dinero en caja cuando procesamos una factura pagada desde el "POS".

## Verification Plan

### Manual Verification
1. Entrar a una orden de reparación válida y presionar "Generar Factura".
2. Constatar que se abre el modal POS.
3. Colocar un monto en efectivo (Ej. $100.000) para un cobro de $60.000, verificar que el cálculo de vuelto sea $40.000 e ingresar el pago.
4. Revisar que la factura quede emitida con saldo cero.
5. Ir a "Facturación" > "Nueva Factura". Introducir productos y cliente.
6. Guardar, presenciar el modal POS, registrar pago y validar que se guarde correctamente en estado Pagado/Emitido.
