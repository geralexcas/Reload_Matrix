import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.abspath("backend"))

from app.core.database import SessionLocal
from app.services.accounting_service import AccountingService

def check_libro():
    db = SessionLocal()
    try:
        service = AccountingService(db)
        result = service.get_libro_compras(company_id=1)
        print("Entries:")
        if "entries" in result:
            for entry in result["entries"]:
                print(entry)
        else:
            print("Error:", result)
    finally:
        db.close()

if __name__ == "__main__":
    check_libro()
