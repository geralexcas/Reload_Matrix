import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.accounting_service import AccountingService

# Use localhost for local direct DB access
engine = create_engine("postgresql://user:password@localhost:5434/business_db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run():
    db = SessionLocal()
    service = AccountingService(db)
    res = service.get_libro_compras(company_id=1)
    if "error" in res:
        print("Error:", res["error"])
    else:
        print("Totals:", res.get("totals"))
    db.close()

if __name__ == "__main__":
    run()
