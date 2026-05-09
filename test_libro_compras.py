import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.accounting_service import AccountingService

engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_libro():
    db = SessionLocal()
    service = AccountingService(db)
    res = service.get_libro_compras(company_id=1)
    print("Result entries count:", len(res.get("entries", [])))
    if "error" in res:
        print("Error:", res["error"])
    else:
        for e in res["entries"]:
            print(f"Inv Number: {e['invoice_number']}, Partner: {e['partner_name']}")
    db.close()

if __name__ == "__main__":
    test_libro()
