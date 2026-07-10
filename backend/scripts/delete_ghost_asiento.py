"""Elimina el asiento contable huerfano de una factura fantasma (factura ya borrada).

Uso:
  python scripts/delete_ghost_asiento.py --invoice-id 7            # dry-run
  python scripts/delete_ghost_asiento.py --invoice-id 7 --force     # ejecuta

Convierte un asiento contable huerfano (journal_entries con reference INV-NNNNNN
cuya factura ya no existe) en su eliminacion limpia, incluyendo lineas y
transacciones de tesoreria/billetera vinculadas.

Seguridad:
  - Sin --force: solo lista que borraria, no toca la BD.
  - Con --force: aborta con error si la factura AUN existe en invoices
    (protege facturas vivas - usa cancel_invoice() para esas).
"""
import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.sql.invoicing import Invoice
from app.models.sql.accounting.journal_entry import JournalEntry
from app.models.sql.accounting.journal_entry_line import JournalEntryLine
from app.models.sql.accounting.treasury_transaction import TreasuryTransaction
from app.models.sql.wallet import WalletTransaction
from sqlalchemy import select, delete, func


def find_ghost(db, invoice_id):
    # ponytail: referencia del servicio es f"INV-{invoice_id:06d}" (accounting_service.py:2365)
    ref = f"INV-{invoice_id:06d}"
    jes = db.execute(
        select(JournalEntry).where(JournalEntry.reference == ref)
    ).scalars().all()
    return ref, jes


def collect_lines(db, je_ids):
    if not je_ids:
        return []
    return db.execute(
        select(JournalEntryLine).where(JournalEntryLine.journal_entry_id.in_(je_ids))
    ).scalars().all()


def collect_treasury(db, je_ids):
    if not je_ids:
        return []
    return db.execute(
        select(TreasuryTransaction).where(
            TreasuryTransaction.journal_entry_id.in_(je_ids)
        )
    ).scalars().all()


def collect_wallet(db, invoice_id):
    return db.execute(
        select(WalletTransaction).where(
            WalletTransaction.reference_type == "INVOICE",
            WalletTransaction.reference_id == invoice_id,
        )
    ).scalars().all()


def main():
    parser = argparse.ArgumentParser(description="Eliminar asiento contable huerfano de factura fantasma.")
    parser.add_argument("--invoice-id", type=int, default=7, help="ID de la factura fantasma (default: 7)")
    parser.add_argument("--force", action="store_true", help="Ejecuta la eliminacion (sin esto es dry-run)")
    args = parser.parse_args()

    invoice_id = args.invoice_id
    db = SessionLocal()
    try:
        # 1. Proteccion: la factura NO debe existir
        invoice = db.execute(
            select(Invoice).where(Invoice.id == invoice_id)
        ).scalar_one_or_none()
        if invoice is not None:
            print(f"ERROR: La factura id={invoice_id} AUN existe (invoice_number={invoice.invoice_number}, "
                  f"status={invoice.status}). Use cancel_invoice() para anularla.")
            print("Abortado: no se borrara el asiento de una factura viva.")
            return

        # 2. Buscar asiento(s) huerfano(s)
        ref, jes = find_ghost(db, invoice_id)
        if not jes:
            print(f"No se encontro ningun asiento contable con reference='{ref}' para la factura id={invoice_id}.")
            print("Nada que limpiar.")
            return

        je_ids = [je.id for je in jes]
        lines = collect_lines(db, je_ids)
        treasury_txs = collect_treasury(db, je_ids)
        wallet_txs = collect_wallet(db, invoice_id)

        # 3. Reporte
        print("=" * 70)
        print(f"Factura fantasma: id={invoice_id} (NO existe en invoices) - OK para limpiar")
        print(f"Referencia del asiento: {ref}")
        print("-" * 70)
        for je in jes:
            print(f"  JE id={je.id} | ref={je.reference} | posted={je.is_posted} | "
                  f"desc={je.description}")
        print(f"  Lineas a borrar: {len(lines)}")
        for ln in lines:
            print(f"    linea id={ln.id} je={ln.journal_entry_id} cuenta={ln.account_id} "
                  f"debit={ln.debit_amount} credito={ln.credit_amount}")
        print(f"  Treasury transactions vinculadas (por journal_entry_id): {len(treasury_txs)}")
        for tt in treasury_txs:
            print(f"    TT id={tt.id} je={tt.journal_entry_id} monto={tt.amount} tipo={tt.transaction_type}")
        print(f"  Wallet transactions vinculadas (reference_type=INVOICE, reference_id={invoice_id}): {len(wallet_txs)}")
        for wt in wallet_txs:
            print(f"    WT id={wt.id} monto={wt.amount} tipo={wt.transaction_type}")
        print("=" * 70)

        if not args.force:
            print("\nDRY-RUN: no se modifico la BD. Re-ejecuta con --force para borrar:")
            print(f"  python scripts/delete_ghost_asiento.py --invoice-id {invoice_id} --force")
            return

        # 4. Ejecucion
        # Treasury primero (FK -> journal_entries), luego lineas, luego JE, luego wallet
        if treasury_txs:
            print("Borrando treasury_transactions...")
            db.execute(
                delete(TreasuryTransaction).where(
                    TreasuryTransaction.journal_entry_id.in_(je_ids)
                )
            )
        if lines:
            print("Borrando journal_entry_lines...")
            db.execute(
                delete(JournalEntryLine).where(
                    JournalEntryLine.journal_entry_id.in_(je_ids)
                )
            )
        print("Borrando journal_entries...")
        db.execute(delete(JournalEntry).where(JournalEntry.id.in_(je_ids)))
        if wallet_txs:
            print("Borrando wallet_transactions...")
            db.execute(
                delete(WalletTransaction).where(
                    WalletTransaction.reference_type == "INVOICE",
                    WalletTransaction.reference_id == invoice_id,
                )
            )

        db.commit()
        print(f"\nOK: asiento(s) huerfano(s) de factura id={invoice_id} eliminado(s). "
              f"{len(jes)} JE, {len(lines)} lineas, {len(treasury_txs)} treasury, "
              f"{len(wallet_txs)} wallet.")
    except Exception as e:
        db.rollback()
        print(f"ERROR al eliminar: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()