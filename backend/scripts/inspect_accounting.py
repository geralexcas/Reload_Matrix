from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.sql.accounting.journal_entry import JournalEntry
from app.core.tenant_context import current_tenant_id

db = SessionLocal()
COMPANY_ID = 25
db.execute(text("SET app.tenant_id = :cid"), {"cid": str(COMPANY_ID)})

entries = db.query(JournalEntry).all()
print(f"--- Asientos contables para empresa {COMPANY_ID} ---")
for e in entries:
    # Calculate total amount from lines (debits)
    total = sum(line.debit_amount for line in e.lines)
    print(f"ID: {e.id}, Desc: {e.description}, Total: {total}, Fecha: {e.created_at}")
    for line in e.lines:
        print(f"  - Cuenta: {line.account_id}, Debe: {line.debit_amount}, Haber: {line.credit_amount}")
db.close()
