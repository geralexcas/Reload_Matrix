# Instrucciones: Registrar Asiento Contable de Gastos

## Acceso

1. Ir a **Contabilidad > Asientos Contables** (`/accounting/journal-entries`)
2. Click en **"Nuevo Asiento"**

---

## Caso 1: Pago de Internet por Transferencia Bancaria

### Datos del encabezado

| Campo | Valor |
|---|---|
| Fecha | Fecha del pago (ej: 2026-06-02) |
| Descripción | `Pago servicio internet junio 2026` |
| Referencia | `TF-0012345` (número de transferencia) |

### Líneas del asiento (debe cuadrar débitos = créditos)

| Línea | Cuenta PUC | Débito | Crédito | Descripción |
|---|---|---|---|---|
| 1 | `5200 - Gastos de administración` | $150,000.00 | 0 | Servicio internet |
| 2 | `111010 - Bancos - Cuenta corriente` | 0 | $150,000.00 | Transferencia bancaria |

> **Lógica contable:** El gasto aumenta (débito en EXPENSE), el banco disminuye (crédito en ASSET). Al publicar, el sistema actualiza automáticamente el `current_balance` del `BankAccount` vinculado a la cuenta `111010` (via `linked_account_id`), y registra un `TreasuryTransaction` tipo WITHDRAWAL.

---

## Caso 2: Pago de Transportes en Efectivo (Caja Principal)

### Datos del encabezado

| Campo | Valor |
|---|---|
| Fecha | Fecha del pago |
| Descripción | `Pago transporte mensual` |
| Referencia | `EFE-001` (o recibo) |

### Líneas del asiento

| Línea | Cuenta PUC | Débito | Crédito | Descripción |
|---|---|---|---|---|
| 1 | `5300 - Gastos de ventas` | $50,000.00 | 0 | Transporte |
| 2 | `111001 - Caja principal` | 0 | $50,000.00 | Salida efectivo |

> **Lógica contable:** El gasto aumenta (débito en EXPENSE), la caja disminuye (crédito en ASSET). Al publicar, el sistema actualiza automáticamente el `current_balance` del `CashAccount` tipo `MAIN_CASH` vinculado a `111001`, y registra un `TreasuryTransaction` tipo WITHDRAWAL.

---

## Reglas clave del sistema

1. **Debe cuadrar**: Total débitos = Total créditos (el formulario lo valida en tiempo real y muestra la diferencia en verde/rojo)
2. **Cada línea**: Solo un campo (débito o crédito) debe ser > 0, el otro queda en 0
3. **Cuentas de gasto** (EXPENSE/COST): Siempre van al **débito** (aumentan con débito)
4. **Cuentas de activo** (ASSET - Bancos/Caja): Siempre van al **crédito** cuando sale dinero (disminuyen con crédito)
5. **Publicación**: El asiento se crea como **Borrador**. Click en el botón verde de "Publicar" (check) para afectar saldos. Una vez publicado **no se puede editar ni eliminar**
6. **Sincronización tesorería**: Al publicar, el servicio `post_journal_entry()` (`accounting_service.py:234`) busca si la cuenta contable tiene un `BankAccount` o `CashAccount` vinculado (por `linked_account_id` o por prefijo de código) y actualiza el saldo automáticamente

---

## PUC disponible por defecto (cuentas relevantes)

| Código | Nombre | Tipo | Uso típico |
|---|---|---|---|
| `111001` | Caja principal | ASSET | Pagos en efectivo |
| `111002` | Caja menor | ASSET | Gastos menores en efectivo |
| `111003` | Caja registro #1 | ASSET | Punto de venta 1 |
| `111004` | Caja registro #2 | ASSET | Punto de venta 2 |
| `111010` | Bancos - Cta. corriente | ASSET | Transferencias/débitos |
| `111011` | Bancos - Cta. ahorros | ASSET | Transferencias de ahorro |
| `111012` | Bancos - Cta. moneda extranjera | ASSET | Cuentas en USD/EUR |
| `5200` | Gastos de administración | EXPENSE | Internet, arriendo, servicios |
| `5300` | Gastos de ventas | EXPENSE | Transporte, publicidad |
| `5400` | Gastos financieros | EXPENSE | Intereses, comisiones |
| `5500` | Gastos por diferencial de cambio | EXPENSE | Pérdidas cambiarias |
| `5600` | Otros gastos | EXPENSE | Gastos varios |

---

## Ejemplo combinado: Internet + Transporte en un solo asiento

| Línea | Cuenta | Débito | Crédito |
|---|---|---|---|
| 1 | 5200 - Gastos administración | $150,000 | 0 |
| 2 | 5300 - Gastos ventas | $50,000 | 0 |
| 3 | 111010 - Bancos cte. | 0 | $150,000 |
| 4 | 111001 - Caja principal | 0 | $50,000 |
| **Total** | | **$200,000** | **$200,000** |

---

## Notas importantes

- Si no ves las cuentas PUC en el dropdown, ejecuta `docker compose exec backend python scripts/init_database.py` para inicializar el plan de cuentas
- Verifica que las cuentas bancarias/cajas en **Tesorería** tengan su `linked_account_id` configurado apuntando a la cuenta PUC correspondiente, para que la sincronización de saldos funcione al publicar
- El `company_id` se toma automáticamente de la sesión del usuario
