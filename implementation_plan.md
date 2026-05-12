# Mejorar Flujo de Facturación desde Reparaciones

El objetivo es optimizar el proceso de generación de facturas a partir de órdenes de reparación, evitando que el dispositivo reparado aparezca automáticamente como un item de venta de $0 y permitiendo la adición manual de servicios y repuestos con precios editables.

## User Review Required

> [!IMPORTANT]
> Se filtrarán automáticamente los items de la reparación que tengan costo $0 y no tengan un producto asociado (que representan el dispositivo recibido). Si por alguna razón un técnico registra un servicio real con costo $0 sin producto, este no aparecerá inicialmente en la factura, pero podrá ser agregado manualmente.

## Proposed Changes

### Frontend

#### [MODIFY] [InvoicingView.vue](file:///home/geralexcas/Reload_Matrix_II/frontend/src/views/Invoicing/InvoicingView.vue)
- **Filtrado de Items:** Actualizar el hook `mounted` para filtrar el item de identificación del equipo (costo $0, sin `product_id`) al importar desde una orden de reparación.
- **Entrada Manual de Servicios:**
    - Modificar `newItem` para incluir `unit_price`.
    - Actualizar `addItem` para permitir agregar items sin `product_id` (servicios manuales).
    - Añadir campo de precio unitario en la barra de "Agregar Productos" cuando no hay un producto seleccionado.
- **Tabla Detalle Editable:**
    - Convertir las celdas de "Descripción" y "Precio Unitario" en campos de entrada (`input`) para permitir ajustes rápidos antes de generar la factura.

## Verification Plan

### Automated Tests
- No aplica (cambios de UI).

### Manual Verification
1. Ir a una Orden de Reparación existente (ej: `/repair/1`).
2. Hacer clic en "Generar Factura".
3. Verificar que el item "CELULAR" (u otro dispositivo) de $0 no aparezca en el detalle de la factura.
4. Intentar agregar un servicio manual (ej: "Limpieza Química") sin seleccionar un producto del buscador, asignándole un precio.
5. Modificar el precio de un repuesto ya agregado directamente en la tabla de detalle.
6. Generar la factura y verificar que los montos y descripciones coincidan en el historial y el PDF.
