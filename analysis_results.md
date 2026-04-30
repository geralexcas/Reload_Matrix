# Auditoría Contable y de Sistema - Reload Matrix

Como experto contador y analista de sistemas, he realizado una revisión exhaustiva del código fuente, con especial atención en el módulo de contabilidad (`accounting_service.py`) y su integración con inventarios y facturación.

He encontrado **incoherencias contables graves** que afectan los saldos en los libros, los reportes de impuestos y la integridad entre los módulos auxiliares y la contabilidad general (Libro Mayor). 

A continuación, detallo los hallazgos críticos que deben ser abordados:

## 1. Duplicación de Registros en Libros Contables (Sobreestimación de Totales)

> [!CAUTION]
> **Riesgo Crítico:** Los reportes de Libro de Compras y Libro de Ventas están inflando los valores totales (compras, ventas e impuestos).

**Análisis Técnico:**
En `accounting_service.py`, al consultar registros que tienen relaciones uno-a-muchos (como `Invoice` con sus `items` o `JournalEntry` con sus `lines`), el sistema utiliza `joinedload()` para optimizar la consulta SQL. Sin embargo, **omite el método `.unique()`** antes de `.all()`. 
Esto provoca que SQLAlchemy devuelva la misma factura o asiento contable tantas veces como líneas tenga asociadas. 

**Prueba:**
En la ejecución del script de pruebas (`test_comprehensive_accounting.py`), se observa que el asiento de stock inicial `SI-000007` aparece dos veces en el Libro de Compras con el mismo monto de $1,000,000, duplicando el total de compras reales.

**Solución:**
Se debe aplicar `.unique()` a todas las consultas con `joinedload` en `accounting_service.py`:
```python
invoices = self.db.query(Invoice).options(...).filter(...).unique().all()
```

---

## 2. Descuadre entre Inventario Físico y Contabilidad (Ausencia de Costo de Ventas - COGS)

> [!WARNING]
> **Riesgo Alto:** El saldo de la cuenta de inventarios (1140) en el Balance de Comprobación crecerá indefinidamente y no reflejará el valor real de la mercancía.

**Análisis Técnico:**
En `inventory_service.py`, el método `create_product` genera correctamente el asiento contable de entrada al inventario (Débito a 1140). Sin embargo, cuando se descuenta el stock para una venta o reparación mediante `deduct_stock()`, **no se genera ningún asiento contable de salida**.

**Consecuencia Contable:**
Toda venta reconoce el "Ingreso" y la "Cuenta por Cobrar/Caja", pero se omite el reconocimiento del **Costo de Ventas (Débito a la 6135)** y la **Salida de Inventario (Crédito a la 1140)**. Al finalizar el mes, los estados financieros mostrarán utilidades irreales (sobreestimadas) porque no se está descontando el costo de la mercancía vendida.

**Solución:**
Modificar `invoicing_service.py` y el cierre de `repair_service` para que, al facturar un producto, se emita un `JournalEntry` que registre el costo de ventas basado en el `purchase_price` del producto.

---

## 3. Pasivos "Fantasma" por Compras de Stock Inicial a Crédito

> [!IMPORTANT]
> **Riesgo Medio:** Inconsistencia entre el módulo de Cuentas por Pagar (Proveedores) y el Libro Mayor.

**Análisis Técnico:**
Cuando se crea un producto en inventario indicando que la forma de pago es "CRÉDITO" (`CREDIT` o `PARTIAL_CREDIT`), el método `create_journal_entry_for_initial_stock` en `accounting_service.py` acredita directamente la cuenta de **Cuentas por pagar (2205)**.

**Consecuencia Contable:**
Aunque la cuenta contable 2205 refleja el pasivo en el Balance General, **no se genera un documento de Compra (`Purchase`) asociado a un proveedor (`Partner`)**. Como resultado:
1. El sistema contable dice que debes dinero.
2. El módulo de Proveedores y Cuentas por Pagar no sabe a quién le debes ni tiene fechas de vencimiento.
3. No podrás registrar el pago de esta deuda desde el módulo de Tesorería porque no hay una factura de compra a la cual aplicarle el recibo de egreso.

**Solución:**
El ingreso de stock inicial a crédito debe forzosamente requerir la selección de un `supplier_id` (Proveedor) y crear automáticamente un documento en el modelo `Purchase` (con estado "ISSUED"), en lugar de hacer solo el asiento manual.

---

## Conclusión y Plan de Acción Sugerido

El sistema tiene una excelente base, pero requiere consolidar la "Partida Doble" en el ciclo de vida completo de los productos. Sugiero que procedamos a reparar estos problemas en el siguiente orden:

1. **Corrección Inmediata:** Añadir `.unique()` a las consultas de `accounting_service.py` para arreglar los reportes fiscales.
2. **Corrección Estructural:** Implementar el registro del **Costo de Ventas (COGS)** cada vez que una factura cambie a estado `ISSUED`.
3. **Mejora de Procesos:** Refinar la lógica de ingreso de "Stock Inicial" para prohibir el crédito "sin proveedor" o forzar la creación de un registro de compra formal.

¿Deseas que comience corrigiendo inmediatamente la duplicación de facturas en los reportes (Punto 1)?
