import os
import sys

# Agrega la raíz de backend a sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.sql.accounting.journal_entry import JournalEntry
from app.models.sql.accounting.journal_entry_line import JournalEntryLine
from app.models.sql.accounting.treasury_transaction import TreasuryTransaction
from sqlalchemy import or_

def cleanup_duplicates():
    db = SessionLocal()
    try:
        # Criterios de búsqueda: Asientos generados por treasury_service con descripciones automáticas de compras, ventas y anulaciones
        conditions = or_(
            JournalEntry.description.like('Pago a proveedor - Factura %'),
            JournalEntry.description.like('Cobro reparación %'),
            JournalEntry.description.like('Pago - Factura %'),
            JournalEntry.description.like('Reversión por anulación de factura %')
        )
        
        # Deben ser asientos de tesorería (DEP- o WDL-)
        ref_conditions = or_(
            JournalEntry.reference.like('DEP-%'),
            JournalEntry.reference.like('WDL-%')
        )

        duplicates = db.query(JournalEntry).filter(
            conditions,
            ref_conditions
        ).all()
        
        print(f"Encontrados {len(duplicates)} registros contables duplicados para limpiar.")
        
        deleted_count = 0
        for je in duplicates:
            print(f"Procesando duplicado: {je.reference} (ID: {je.id}) - Desc: {je.description}")
            
            # 1. Actualizar transacciones de tesorería que apuntan a este JE duplicado
            txs = db.query(TreasuryTransaction).filter(TreasuryTransaction.journal_entry_id == je.id).all()
            for tx in txs:
                # Desvinculamos el asiento duplicado de la transacción de tesorería.
                # (El asiento principal de la factura/compra ya contiene el movimiento de caja correcto)
                tx.journal_entry_id = None
                print(f"  -> Transacción de tesorería {tx.id} desvinculada del asiento {je.id}")
            
            # 2. Eliminar líneas del asiento duplicado
            lines_deleted = db.query(JournalEntryLine).filter(JournalEntryLine.journal_entry_id == je.id).delete()
            print(f"  -> {lines_deleted} líneas de asiento eliminadas")
            
            # 3. Eliminar el asiento duplicado
            db.delete(je)
            deleted_count += 1
            
        db.commit()
        print(f"Limpieza completada exitosamente. {deleted_count} asientos contables duplicados fueron eliminados.")
        
    except Exception as e:
        db.rollback()
        print(f"Error crítico durante la limpieza: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_duplicates()
