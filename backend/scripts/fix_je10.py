import sys
sys.path.append("/app")
from app.core.database import SessionLocal
from app.models.sql.accounting.journal_entry import JournalEntry
from app.models.sql.accounting.journal_entry_line import JournalEntryLine
from app.models.sql.accounting.treasury_transaction import TreasuryTransaction
from sqlalchemy import delete

def fix():
    db = SessionLocal()
    try:
        # Delete double counting journal entry
        je = db.query(JournalEntry).filter(JournalEntry.id == 10).first()
        if je:
            db.execute(delete(JournalEntryLine).where(JournalEntryLine.journal_entry_id == 10))
            db.delete(je)
            
        # Delete the treasury transaction
        tt = db.query(TreasuryTransaction).filter(TreasuryTransaction.journal_entry_id == 10).first()
        if tt:
            db.delete(tt)
            
        # Also fix the cash account balance which got inflated
        from app.models.sql.treasury import CashAccount
        cash = db.query(CashAccount).filter(CashAccount.id == 1).first()
        if cash:
            # We know it deposited 436554.63 erroneously
            cash.current_balance -= 436554.63
            
        db.commit()
        print("Fixed duplicate reversal logic.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix()
