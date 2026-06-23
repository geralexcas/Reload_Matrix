## Solución al problema de los informes contables y sincronización de tesorería

### Contexto
El cliente reportó que en la ruta **/accounting/libro-ventas** se mostraba el total de ingresos correcto ($266.000), mientras que en **/accounting/estado-resultados** solo aparecían $1.000, lo que indicaba que los costos y gastos no estaban siendo contabilizados. Además, un test unitario (`TestPostJournalEntryTreasurySync.test_post_creates_treasury_transaction_when_linked`) fallaba porque la publicación de asientos contables no sincronizaba correctamente con las cuentas de tesorería.

### Diagnóstico
1. **Libro de ventas/compras** consulta directamente la tabla `Invoice`. Por eso mostraba los valores correctos.
2. **Estado de Resultados** se basa en los saldos de `JournalEntryLine` filtrados por `account_type` (REVENUE, COST, EXPENSE). Los asientos de costo (`6135` o `5100`) no existían porque las facturas de muestra se creaban sin ítems y, por tanto, sin `product_id`. El método `create_journal_entry_from_invoice` solo genera la línea de costo cuando `total_cost > 0`.
3. En `AccountingService.post_journal_entry` había un `continue` prematuro que descartaba la búsqueda de una cuenta de efectivo cuando no se encontraba una cuenta bancaria vinculada, impidiendo que el test verificara la sincronización con tesorería.

### Solución implementada
#### 1. Corrección del script de seed
- Se modificó `backend/app/seed_accounting.py`:
  - En `create_sample_invoice` ahora se crea una factura **con ítems** usando el esquema `InvoiceWithItemsCreate`.
  - Se incluye `product_id` en el ítem para que el cálculo de `total_cost` sea posible y se genere la línea de costo (`6135`).
  - Se utiliza `InvoicingService.create_invoice_with_items` para crear la factura y sus ítems en una única transacción.
- Commit: `fix: create invoice with items in seed script to generate cost lines`.

#### 2. Mejora de la sincronización con tesorería
- En `backend/app/services/accounting_service.py` se refactorizó el bloque que buscaba cuentas bancarias y de efectivo:
  - Se eliminó el `continue` que terminaba la iteración antes de intentar buscar una cuenta de efectivo.
  - Se añadió lógica para **buscar todas las cuentas bancarias/cajas activas** y comparar sus códigos COA con el código de la línea del asiento. Si se encuentra coincidencia se asigna la cuenta.
  - Se agregó un comentario explicativo y se reorganizó el flujo para que, si no se encuentra ninguna cuenta vinculada, se continúe con la siguiente línea.
- Se actualizó también la sección de manejo de cuentas de efectivo con la misma lógica de búsqueda y un `continue` solo cuando no se halló ninguna cuenta.

#### 3. Verificación
- Ejecuté `docker compose exec backend pytest -q` y todos los **65 tests pasaron** (`65 passed, 12 warnings`).
- Consulté manualmente los datos:
  ```bash
  docker compose exec backend python - <<'PY'
  from app.core.database import SessionLocal
  from app.services.accounting_service import AccountingService
  db = SessionLocal()
  print(AccountingService(db).get_estado_resultados(company_id=1))
  PY
  ```
  El resultado muestra ingresos, costos, gastos y utilidades correctas.
- Se comprobó que al publicar un asiento con líneas que afectan cuentas de tesorería ahora se crea al menos una `TreasuryTransaction` y el campo `treasury_sync_count` es mayor o igual a 1.

### Resultado final
- **Estado de Resultados** muestra los valores reales (ingresos, costos, gastos, utilidad bruta y neta) gracias a los asientos de costo generados.
- La sincronización con tesorería funciona y los tests relacionados pasan.
- El script de seed ahora genera datos de ejemplo totalmente funcionales para futuros desarrollos y pruebas.

---
**Pasos para reproducir**
1. Levantar los contenedores (`docker compose up --build`).
2. Ejecutar el script de seed:
   ```bash
   docker compose exec backend python /app/app/seed_accounting.py
   ```
3. Consultar los endpoints o ejecutar los tests.

---
**Nota**: Los cambios se encuentran en los archivos:
- `backend/app/seed_accounting.py`
- `backend/app/services/accounting_service.py`

---
**Próximos pasos sugeridos**
- Añadir pruebas unitarias para validar que la lógica de búsqueda de cuentas bancarias/cajas cubra casos con códigos COA parciales.
- Documentar en la wiki interna la necesidad de crear siempre facturas con ítems para asegurar la correcta generación de costos.
