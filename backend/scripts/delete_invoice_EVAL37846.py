import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.sql.invoicing import Invoice, InvoiceItem
from app.models.sql.accounting.journal_entry import JournalEntry
from app.models.sql.accounting.journal_entry_line import JournalEntryLine
from app.models.sql.accounting.treasury_transaction import TreasuryTransaction
from app.models.sql.wallet import WalletTransaction
from app.models.sql.credit_debit_notes import CreditDebitNote
from app.models.sql.repair import RepairOrder
from app.models.sql.inventory_movement import InventoryMovement, InventoryMovementType
from app.models.sql.inventory import Product
from app.models.sql.partners import Partner
from sqlalchemy import text

INVOICE_NUMBER = "EVAL37846"


def main():
    import argparse
    parser = argparse.ArgumentParser(description=f"Eliminar factura {INVOICE_NUMBER} y todo rastro.")
    parser.add_argument("--force", action="store_true", help="Ejecuta la eliminacion (sin esto es dry-run)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        invoice = db.query(Invoice).filter(
            Invoice.invoice_number == INVOICE_NUMBER
        ).first()

        if not invoice:
            print(f"ERROR: No se encontro factura con numero '{INVOICE_NUMBER}'")
            return

        invoice_id = invoice.id
        company_id = invoice.company_id
        ref = f"INV-{invoice_id:06d}"

        print("=" * 70)
        print(f"Factura:  {INVOICE_NUMBER} (id={invoice_id})")
        print(f"Company:  id={company_id}")
        print(f"Status:   {invoice.status}")
        print(f"Total:    {invoice.total_amount}")
        print(f"Creada:   {invoice.created_at}")

        partner = db.query(Partner).filter(Partner.id == invoice.partner_id).first()
        print(f"Socio:    {partner.name if partner else 'N/A'} (id={invoice.partner_id})")
        print("-" * 70)

        invoice_items = db.query(InvoiceItem).filter(
            InvoiceItem.invoice_id == invoice_id
        ).all()
        print(f"Invoice Items: {len(invoice_items)} lineas")
        for it in invoice_items:
            print(f"  - product_id={it.product_id} qty={it.quantity} total={it.line_total}")

        jes = db.query(JournalEntry).filter(
            JournalEntry.reference.in_([ref, f"REV-{ref}"])
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
            print(f"  - linea id={ln.id} je={ln.journal_entry_id} cuenta={ln.account_id} "
                  f"debit={ln.debit_amount} credit={ln.credit_amount}")

        treasury_txs = db.query(TreasuryTransaction).filter(
            TreasuryTransaction.reference == ref
        ).all()
        print(f"Treasury Transactions: {len(treasury_txs)}")
        for tt in treasury_txs:
            print(f"  - TT id={tt.id} ref={tt.reference} monto={tt.amount} tipo={tt.transaction_type}")

        wallet_txs = db.query(WalletTransaction).filter(
            WalletTransaction.reference_type == "INVOICE",
            WalletTransaction.reference_id == invoice_id,
        ).all()
        print(f"Wallet Transactions: {len(wallet_txs)}")
        for wt in wallet_txs:
            print(f"  - WT id={wt.id} monto={wt.amount} tipo={wt.transaction_type}")

        notes = db.query(CreditDebitNote).filter(
            CreditDebitNote.original_invoice_id == invoice_id
        ).all()
        print(f"Credit/Debit Notes: {len(notes)}")
        for n in notes:
            print(f"  - nota id={n.id} tipo={n.note_type} monto={n.amount}")

        repairs = db.query(RepairOrder).filter(
            RepairOrder.invoice_id == invoice_id
        ).all()
        print(f"Repair Orders (desvincular): {len(repairs)}")
        for r in repairs:
            print(f"  - RO id={r.id}")

        inv_movements = _find_inventory_movements(db, invoice, invoice_items)
        print(f"Inventory Movements (DEDUCT): {len(inv_movements)}")
        for im in inv_movements:
            print(f"  - IM id={im.id} product_id={im.product_id} qty={im.quantity} created={im.created_at}")

        print("=" * 70)

        if not args.force:
            print("\nDRY-RUN: no se modifico la BD.")
            print(f"Re-ejecuta con --force para eliminar:\n  python scripts/delete_invoice_EVAL37846.py --force")
            return

        confirm = input("\n\u00bfELIMINAR todo lo anterior? (s/n): ")
        if confirm.lower() != "s":
            print("Cancelado.")
            return

        _execute_deletion(db, invoice_id, je_ids, lines, treasury_txs,
                          wallet_txs, notes, repairs, inv_movements, invoice_items, company_id)

        print(f"\nOK: factura {INVOICE_NUMBER} eliminada completamente.")

    except Exception as e:
        db.rollback()
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def _find_inventory_movements(db, invoice, invoice_items):
    movements = []
    for item in invoice_items:
        candidates = db.query(InventoryMovement).filter(
            InventoryMovement.product_id == item.product_id,
            InventoryMovement.movement_type == InventoryMovementType.DEDUCT,
            InventoryMovement.quantity == item.quantity,
            InventoryMovement.company_id == invoice.company_id,
        ).order_by(InventoryMovement.created_at.desc()).all()

        closest = None
        for c in candidates:
            if c.created_at and invoice.created_at:
                delta = abs((c.created_at - invoice.created_at).total_seconds())
                if delta <= 300:
                    closest = c
                    break
        if closest:
            movements.append(closest)
    return movements


def _execute_deletion(db, invoice_id, je_ids, lines, treasury_txs,
                      wallet_txs, notes, repairs, inv_movements, invoice_items, company_id):
    # Set tenant context
    db.execute(text(f"SET app.tenant_id = '{company_id}'"))

    # 1. Journal entry lines
    if je_ids:
        deleted = db.query(JournalEntryLine).filter(
            JournalEntryLine.journal_entry_id.in_(je_ids)
        ).delete(synchronize_session=False)
        print(f"  Borradas {deleted} journal_entry_lines")

    # 2. Treasury transactions
    for tt in treasury_txs:
        db.delete(tt)
        print(f"  Borrada treasury_transaction id={tt.id}")

    # 3. Journal entries
    for je in db.query(JournalEntry).filter(JournalEntry.id.in_(je_ids)).all():
        db.delete(je)
        print(f"  Borrado JournalEntry id={je.id} ref={je.reference}")

    # 4. Wallet transactions
    for wt in wallet_txs:
        db.delete(wt)
        print(f"  Borrada WalletTransaction id={wt.id}")

    # 5. Credit/debit notes
    for n in notes:
        db.delete(n)
        print(f"  Borrada CreditDebitNote id={n.id}")

    # 6. Repair orders (desvincular)
    for r in repairs:
        r.invoice_id = None
        print(f"  Desvinculada RepairOrder id={r.id}")

    # 7. Inventory movements + restore stock
    for im in inv_movements:
        product = db.query(Product).filter(Product.id == im.product_id).first()
        if product:
            product.quantity = (product.quantity or 0) + (im.quantity or 0)
            print(f"  Stock restaurado: product_id={im.product_id} +{im.quantity} (ahora {product.quantity})")
        db.delete(im)
        print(f"  Borrado InventoryMovement id={im.id}")

    # 8. Invoice items
    for it in invoice_items:
        db.delete(it)
        print(f"  Borrado InvoiceItem id={it.id}")

    # 9. Invoice
    db.execute(text("DELETE FROM invoices WHERE id = :id"), {"id": invoice_id})
    print(f"  Borrada Invoice id={invoice_id}")

    db.commit()


if __name__ == "__main__":
    main()