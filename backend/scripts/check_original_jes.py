import sys
sys.path.append("/app")
from app.core.database import SessionLocal
from app.models.sql.accounting.journal_entry import JournalEntry
from app.models.sql.accounting.chart_of_accounts import ChartOfAccounts

def check():
    db = SessionLocal()
    try:
        jes = db.query(JournalEntry).order_by(JournalEntry.id).all()
        for je in jes:
            print(f"JE {je.id}: Ref={je.reference} | Desc={je.description}")
            for line in je.lines:
                acc = db.query(ChartOfAccounts).filter(ChartOfAccounts.id == line.account_id).first()
                print(f"  [{acc.code if acc else '?'}] {acc.name if acc else '?'} | D: {line.debit_amount} | C: {line.credit_amount}")
            print("-" * 40)
    finally:
        db.close()

if __name__ == "__main__":
    check()
