import os
import sys

# Agrega la raíz de backend a sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.sql.accounting.journal_entry import JournalEntry
from app.models.sql.accounting.journal_entry_line import JournalEntryLine
from app.models.sql.accounting.treasury_transaction import TreasuryTransaction

def cleanup_duplicates():
    db = SessionLocal()
    try:
        # 1. Encontrar todos los JournalEntry duplicados generados por TreasuryService
        # Tienen descripción que comienza con "Stock inicial - " pero NO con "Stock inicial producto - "
        duplicates = db.query(JournalEntry).filter(
            JournalEntry.reference.like('SI-%'),
            JournalEntry.description.like('Stock inicial - %')
        ).all()
        
        print(f"Encontrados {len(duplicates)} registros contables duplicados para limpiar.")
        
        deleted_count = 0
        for je in duplicates:
            print(f"Procesando duplicado: {je.reference} (ID: {je.id})")
            
            # Buscar si existe el JournalEntry correcto (el generado por AccountingService)
            # que tiene descripción "Stock inicial producto - ..."
            correct_je = db.query(JournalEntry).filter(
                JournalEntry.reference == je.reference,
                JournalEntry.description.like('Stock inicial producto - %')
            ).first()
            
            # 2. Actualizar transacciones de tesorería que apuntan a este JE duplicado
            txs = db.query(TreasuryTransaction).filter(TreasuryTransaction.journal_entry_id == je.id).all()
            for tx in txs:
                if correct_je:
                    tx.journal_entry_id = correct_je.id
                    print(f"  -> Transacción de tesorería {tx.id} enlazada al asiento contable correcto (ID: {correct_je.id})")
                else:
                    tx.journal_entry_id = None
                    print(f"  -> Transacción de tesorería {tx.id} desvinculada (no se encontró asiento principal)")
            
            # 3. Eliminar líneas del asiento duplicado
            lines_deleted = db.query(JournalEntryLine).filter(JournalEntryLine.journal_entry_id == je.id).delete()
            print(f"  -> {lines_deleted} líneas de asiento eliminadas")
            
            # 4. Eliminar el asiento duplicado
            db.delete(je)
            deleted_count += 1
            
        db.commit()
        print(f"Limpieza completada. {deleted_count} asientos contables duplicados fueron eliminados.")
        
    except Exception as e:
        db.rollback()
        print(f"Error durante la limpieza: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_duplicates()
