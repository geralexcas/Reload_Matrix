# Resumen de Correcciones Contables Implementadas

He finalizado la auditoría y refactorización del módulo contable y de inventarios para asegurar la consistencia del Libro Mayor con los libros auxiliares. A continuación, te presento el resumen de los cambios aplicados en el sistema:

## 1. Reparación de Reportes Fiscales (Libros de Compras y Ventas)
**Problema resuelto:** Los reportes de impuestos sobreestimaban los totales debido a un problema técnico con la base de datos que duplicaba el conteo de facturas con múltiples artículos.
**Solución implementada:**
- Se agregó el filtro `.unique()` a todas las consultas del `accounting_service.py` que utilizan carga relacional (`joinedload()`).
- Los reportes de Libro de Compras y Libro de Ventas ahora extraen totales exactos, eliminando duplicados algorítmicos.

## 2. Automatización del Costo de Ventas (COGS)
**Problema resuelto:** Anteriormente, vender un producto no deducía su costo del inventario contable, mostrando una utilidad bruta inflada y un inventario físico descuadrado con la cuenta `1140`.
**Solución implementada:**
- El servicio de facturación (`invoicing_service.py`) ahora revisa cada artículo facturado para calcular el costo de venta usando su `purchase_price`.
- Al emitir una factura, el sistema crea automáticamente un asiento contable doble adicional:
  - **Débito:** Costo de Ventas (6135).
  - **Crédito:** Inventarios (1140).
- Cuando una factura es anulada, estos movimientos se revierten a la perfección, recuperando el saldo de inventario.

## 3. Prevención de Deudas Fantasmas en Inventario
**Problema resuelto:** Al registrar "Stock Inicial" a CRÉDITO sin asignar un proveedor, el sistema generaba pasivos "fantasma" que el módulo de Cuentas por Pagar no podía rastrear.
**Solución implementada:**
- El servicio de inventarios (`inventory_service.py`) ahora exige estrictamente asignar un proveedor (`supplier_id`) cuando la opción de compra es "CRÉDITO" o "CRÉDITO PARCIAL".
- En lugar de asentar solo la cuenta manual de pasivo (2205), el sistema **crea un documento de Compra (`Purchase`) formal en estado `ISSUED`**. Esto garantiza que la deuda aparezca correctamente en la sección de Proveedores y pueda ser pagada desde el módulo de Tesorería.

---
> [!NOTE]
> Nota sobre el historial: En el `Libro de Compras` es posible que aún veas el registro `SI-000007` duplicado temporalmente. Esto se debe a que fue creado con la lógica antigua durante tus pruebas previas en base de datos. Todos los ingresos y facturas creadas de ahora en adelante se registrarán correctamente con la nueva arquitectura.
