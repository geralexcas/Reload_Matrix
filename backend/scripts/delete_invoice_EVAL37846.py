import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.sql.purchases import Purchase, PurchaseItem, PurchasePayment
from app.models.sql.accounting.journal_entry import JournalEntry
from app.models.sql.accounting.journal_entry_line import JournalEntryLine
from app.models.sql.accounting.treasury_transaction import TreasuryTransaction
from app.models.sql.inventory_movement import InventoryMovement
from app.models.sql.partners import Partner
from sqlalchemy import text

PURCHASE_NUMBER = "EVAL37846"


def main():
    import argparse
    parser = argparse.ArgumentParser(description=f"Eliminar compra {PURCHASE_NUMBER} y todo rastro.")
    parser.add_argument("--force", action="store_true", help="Ejecuta la eliminacion (sin esto es dry-run)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        purchase = db.query(Purchase).filter(
            Purchase.purchase_number == PURCHASE_NUMBER
        ).first()

        if not purchase:
            print(f"ERROR: No se encontro compra con numero '{PURCHASE_NUMBER}'")
            return

        purchase_id = purchase.id
        company_id = purchase.company_id
        cp_ref = f"CP-{purchase_id:06d}"
        pur_ref = f"PUR-{purchase_id:06d}"

        print("=" * 70)
        print(f"Compra:     {PURCHASE_NUMBER} (id={purchase_id})")
        print(f"Company:    id={company_id}")
        print(f"Status:     {purchase.status}")
        print(f"Total:      {purchase.total_amount}")
        print(f"Fecha:      {purchase.purchase_date}")

        partner = db.query(Partner).filter(Partner.id == purchase.partner_id).first()
        print(f"Proveedor:  {partner.name if partner else 'N/A'} (id={purchase.partner_id})")
        print("-" * 70)

        items = db.query(PurchaseItem).filter(
            PurchaseItem.purchase_id == purchase_id
        ).all()
        print(f"Purchase Items: {len(items)} lineas")
        for it in items:
            print(f"  - product_id={it.product_id} qty={it.quantity} precio={it.unit_price} total={it.line_total}")

        payments = db.query(PurchasePayment).filter(
            PurchasePayment.purchase_id == purchase_id
        ).all()
        print(f"Purchase Payments: {len(payments)}")
        for p in payments:
            print(f"  - id={p.id} metodo={p.payment_method} monto={p.amount} ref={p.reference}")

        jes = db.query(JournalEntry).filter(
            JournalEntry.reference == cp_ref
        ).all()
        je_ids = [je.id for je in jes]
        print(f"Journal Entries: {len(jes)}")
        for je in jes:
            print(f"  - JE id={je.id} ref={je.reference} posted={je.is_posted} desc={je.description}")

        lines = []
        if je_ids:
            lines = db.query(JournalEntryLine).filter(
                JournalEntryLine.journal_entry_id.in_(je_ids)
            ).all()
        print(f"Journal Entry Lines: {len(lines)}")
        for ln in lines:
            print(f"  - id={ln.id} je={ln.journal_entry_id} cuenta={ln.account_id} "
                  f"debit={ln.debit_amount} credit={ln.credit_amount}")

        treasury_txs = db.query(TreasuryTransaction).filter(
            TreasuryTransaction.reference == f"Auto-{PURCHASE_NUMBER}"
        ).all()
        print(f"Treasury Transactions: {len(treasury_txs)}")
        for tt in treasury_txs:
            print(f"  - TT id={tt.id} ref={tt.reference} monto={tt.amount} tipo={tt.transaction_type}")

        inv_movements = db.query(InventoryMovement).filter(
            InventoryMovement.reference == pur_ref
        ).all()
        print(f"Inventory Movements: {len(inv_movements)}")
        for im in inv_movements:
            print(f"  - IM id={im.id} product_id={im.product_id} tipo={im.movement_type} qty={im.quantity}")

        print("=" * 70)

        if not args.force:
            print("\nDRY-RUN: no se modifico la BD.")
            print(f"Re-ejecuta con --force para eliminar:\n  python scripts/delete_invoice_EVAL37846.py --force")
            return

        confirm = input("\n\u00bfELIMINAR todo lo anterior? (s/n): ")
        if confirm.lower() != "s":
            print("Cancelado.")
            return

        _execute_deletion(db, purchase_id, je_ids, lines, treasury_txs,
                          inv_movements, items, payments, company_id)

        print(f"\nOK: compra {PURCHASE_NUMBER} eliminada completamente.")

    except Exception as e:
        db.rollback()
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def _execute_deletion(db, purchase_id, je_ids, lines, treasury_txs,
                      inv_movements, items, payments, company_id):
    db.execute(text(f"SET app.tenant_id = '{company_id}'"))

    # 1. Journal entry lines
    if je_ids:
        placeholders = ",".join([f":je{i}" for i in range(len(je_ids))])
        params = {f"je{i}": je_id for i, je_id in enumerate(je_ids)}
        result = db.execute(text(f"DELETE FROM journal_entry_lines WHERE journal_entry_id IN ({placeholders})"), params)
        print(f"  Borradas {result.rowcount} journal_entry_lines")

    # 2. Inventory movements (revertir stock)
    for im in inv_movements:
        if im.movement_type and im.movement_type.value == "ADD":
            db.execute(
                text("UPDATE products SET quantity = quantity - :qty WHERE id = :pid"),
                {"qty": float(im.quantity or 0), "pid": im.product_id}
            )
            print(f"  Stock revertido: product_id={im.product_id} -{im.quantity}")
    if inv_movements:
        im_ids = [im.id for im in inv_movements]
        placeholders = ",".join([f":im{i}" for i in range(len(im_ids))])
        params = {f"im{i}": im_id for i, im_id in enumerate(im_ids)}
        result = db.execute(text(f"DELETE FROM inventory_movements WHERE id IN ({placeholders})"), params)
        print(f"  Borrados {result.rowcount} inventory_movements")

    # 3. Treasury transactions
    if treasury_txs:
        tt_ids = [tt.id for tt in treasury_txs]
        placeholders = ",".join([f":tt{i}" for i in range(len(tt_ids))])
        params = {f"tt{i}": tt_id for i, tt_id in enumerate(tt_ids)}
        result = db.execute(text(f"DELETE FROM treasury_transactions WHERE id IN ({placeholders})"), params)
        print(f"  Borradas {result.rowcount} treasury_transactions")

    # 4. Journal entries
    if je_ids:
        placeholders = ",".join([f":je{i}" for i in range(len(je_ids))])
        params = {f"je{i}": je_id for i, je_id in enumerate(je_ids)}
        result = db.execute(text(f"DELETE FROM journal_entries WHERE id IN ({placeholders})"), params)
        print(f"  Borrados {result.rowcount} journal_entries")

    # 5. Purchase payments
    if payments:
        pay_ids = [p.id for p in payments]
        placeholders = ",".join([f":pay{i}" for i in range(len(pay_ids))])
        params = {f"pay{i}": pay_id for i, pay_id in enumerate(pay_ids)}
        result = db.execute(text(f"DELETE FROM purchase_payments WHERE id IN ({placeholders})"), params)
        print(f"  Borradas {result.rowcount} purchase_payments")

    # 6. Purchase items
    if items:
        it_ids = [it.id for it in items]
        placeholders = ",".join([f":it{i}" for i in range(len(it_ids))])
        params = {f"it{i}": it_id for i, it_id in enumerate(it_ids)}
        result = db.execute(text(f"DELETE FROM purchase_items WHERE id IN ({placeholders})"), params)
        print(f"  Borrados {result.rowcount} purchase_items")

    # 7. Purchase
    result = db.execute(text("DELETE FROM purchases WHERE id = :id"), {"id": purchase_id})
    print(f"  Borrada Purchase id={purchase_id} (rows={result.rowcount})")

    db.commit()


if __name__ == "__main__":
    main()
