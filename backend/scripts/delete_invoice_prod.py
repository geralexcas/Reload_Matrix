import sys
import os

# Agregamos el directorio backend al sys.path para poder importar los modulos de la app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.sql.invoicing import Invoice, InvoiceItem
from app.models.sql.accounting.journal_entry import JournalEntry
from app.models.sql.accounting.journal_entry_line import JournalEntryLine
from app.models.sql.accounting.treasury_transaction import TreasuryTransaction
from app.models.sql.wallet import WalletTransaction
from sqlalchemy import select, delete

def main():
    db = SessionLocal()
    try:
        print("Iniciando busqueda de la factura INV-00000007...")
        # Buscar la factura
        invoice_query = select(Invoice).where(Invoice.invoice_number == "INV-00000007")
        invoice = db.execute(invoice_query).scalar_one_or_none()
        
        if not invoice:
            print("Factura INV-00000007 no encontrada en la base de datos.")
            return

        print(f"Factura encontrada: ID {invoice.id}, Total {invoice.total_amount}")

        # Buscar y eliminar Asientos Contables (y sus lineas por cascade)
        je_query = select(JournalEntry).where(JournalEntry.reference == "INV-00000007")
        journal_entries = db.execute(je_query).scalars().all()
        
        for je in journal_entries:
            print(f"Eliminando Asiento Contable ID: {je.id}")
            # Eliminar las lineas primero (aunque deberia hacer cascade, es mas seguro asi en SQL Alchemy basico)
            db.execute(delete(JournalEntryLine).where(JournalEntryLine.journal_entry_id == je.id))
            # Eliminar el Asiento Contable
            db.execute(delete(JournalEntry).where(JournalEntry.id == je.id))

        # Buscar y eliminar Transacciones de Tesoreria
        tt_query = select(TreasuryTransaction).where(TreasuryTransaction.reference == "INV-00000007")
        treasury_txs = db.execute(tt_query).scalars().all()
        for tt in treasury_txs:
            print(f"Eliminando Transaccion de Tesoreria ID: {tt.id}")
            db.execute(delete(TreasuryTransaction).where(TreasuryTransaction.id == tt.id))

        # Buscar y eliminar Transacciones de Billetera (Si aplica, donde reference_id sea la factura)
        wt_query = select(WalletTransaction).where(
            WalletTransaction.reference_id == invoice.id, 
            WalletTransaction.reference_type == "INVOICE"
        )
        wallet_txs = db.execute(wt_query).scalars().all()
        for wt in wallet_txs:
            print(f"Eliminando Transaccion de Billetera ID: {wt.id}")
            db.execute(delete(WalletTransaction).where(WalletTransaction.id == wt.id))

        # Eliminar items de la factura
        print(f"Eliminando items de la factura {invoice.id}...")
        db.execute(delete(InvoiceItem).where(InvoiceItem.invoice_id == invoice.id))

        # Eliminar la factura
        print(f"Eliminando factura {invoice.id}...")
        db.execute(delete(Invoice).where(Invoice.id == invoice.id))

        db.commit()
        print("Eliminacion de la factura y todo su rastro contable completada con exito.")
    except Exception as e:
        db.rollback()
        print(f"Ocurrio un error al intentar eliminar los registros: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
