import sys
import os
sys.path.append("/app")

from app.core.database import SessionLocal
from app.models.sql.accounting.journal_entry import JournalEntry
from sqlalchemy import or_

def verify_accounting():
    db = SessionLocal()
    try:
        # Buscar asientos que puedan estar relacionados con la compra eliminada
        # Ya sea por descripcion o por referencia de reversion
        jes = db.query(JournalEntry).filter(
            or_(
                JournalEntry.description.ilike('%FECO 66687%'),
                JournalEntry.description.ilike('%Anulación de compra%')
            )
        ).all()
        
        print(f"=========================================")
        print(f"VERIFICACIÓN DE ASIENTOS CONTABLES")
        print(f"=========================================\n")
        
        if not jes:
            print("No se encontraron asientos contables en la base de datos relacionados con FECO 66687.")
            print("Si eliminaste la compra completamente de la base de datos (hard delete), los asientos contables relacionados debieron eliminarse también (ya sea manualmente o por cascada).")
        else:
            print(f"Se encontraron {len(jes)} asiento(s) contable(s):\n")
            for je in jes:
                print(f"Asiento ID: {je.id}")
                print(f"Referencia: {je.reference}")
                print(f"Descripción: {je.description}")
                print(f"Estado: {'Contabilizado' if je.is_posted else 'Borrador'}")
                
                total_debit = sum(line.debit_amount for line in je.lines)
                total_credit = sum(line.credit_amount for line in je.lines)
                
                print(f"Líneas del Asiento:")
                for line in je.lines:
                    account_code = line.account.code if line.account else "N/A"
                    print(f"  - Cta {account_code}: Débito ${line.debit_amount} | Crédito ${line.credit_amount} ({line.description})")
                print(f"Total Débitos: ${total_debit} | Total Créditos: ${total_credit}")
                print("-" * 40)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_accounting()
