from app.core.database import SessionLocal
from app.models.sql.accounting.journal_entry import JournalEntry
from app.models.sql.accounting.journal_entry_line import JournalEntryLine
from app.models.sql.accounting.chart_of_accounts import ChartOfAccounts

def debug_jes():
    db = SessionLocal()
    jes = db.query(JournalEntry).all()
    print(f"Total Asientos: {len(jes)}")
    
    for je in jes:
        print(f"\nAsiento ID: {je.id}")
        print(f"  Fecha: {je.entry_date}")
        print(f"  Publicado: {je.is_posted}")
        print(f"  Referencia: {je.reference}")
        print(f"  Empresa ID: {je.company_id}")
        
        lines = db.query(JournalEntryLine).filter(JournalEntryLine.journal_entry_id == je.id).all()
        for l in lines:
            acc = db.query(ChartOfAccounts).filter(ChartOfAccounts.id == l.account_id).first()
            acc_code = acc.code if acc else "???"
            acc_name = acc.name if acc else "???"
            print(f"    - Cuenta: {acc_code} ({acc_name}) | D: {l.debit_amount} | C: {l.credit_amount}")
            
    db.close()

if __name__ == "__main__":
    debug_jes()
