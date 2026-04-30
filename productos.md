# Plan: Creación de Productos con Movimientos Contables

## Objetivo
Cuando se crea un producto con stock inicial desde `/inventory/new`, reflejar automáticamente en la contabilidad profesional.

## Flujo Requerido (como Compras/Purchases)

| Paso | Acción | Reference Code |
|------|---------|----------------|
| 1. Crear Producto | ✅ Guardar en BD | - |
| 2. Accounting Journal Entry | Débito: Inventario (1140), Crédito: según payment_method | `SI-{id:06d}` |
| 3. Treasury Transaction | Descontar de Caja/Banco según payment_method | `SI-{id:06d}` |

---

## Lógica por Método de Pago

| payment_method | Crédito Contable | Treasury |
|----------------|-----------------|----------|
| CASH (Efectivo) | Caja (111001) | withdraw() de Caja |
| BANK_TRANSFER | Banco (111010) | withdraw() de Banco |
| CREDIT | Cuentas por Pagar (2205) | **NO** crear (pendiente) |

---

## Archivos a Modificar

### 1. `backend/app/services/inventory_service.py`

**Agregar después de línea 43:**

```python
# Create treasury transaction if not CREDIT
payment_method_str = "CASH" if not product.payment_method else (
    product.payment_method.value if hasattr(product.payment_method, 'value') else str(product.payment_method)
)

if payment_method_str not in ["CREDIT"] and db_product.stock_level > 0 and db_product.purchase_price > 0:
    try:
        treasury_service = TreasuryService(self.db)
        account_type = "CASH" if payment_method_str == "CASH" else "BANK"
        
        accounts = treasury_service.get_cash_accounts(company_id) if account_type == "CASH" \
                   else treasury_service.get_bank_accounts(company_id)
        
        if accounts:
            treasury_service.withdraw(
                account_id=accounts[0].id,
                amount=db_product.stock_level * db_product.purchase_price,
                reference=f"SI-{db_product.id:06d}",
                description=f"Stock inicial - {db_product.name}",
                company_id=company_id
            )
    except Exception as e:
        logging.error(f"Error creating treasury transaction: {e}")
```

---

## Nota Técnica

- El journal entry ya se crea con `create_journal_entry_for_initial_stock`
- Solo falta agregar la llamada a TreasuryService
- El código de referencia debe ser `SI-{product_id:06d}` (Stock Inicial)