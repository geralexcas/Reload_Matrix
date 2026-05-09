import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.accounting_service import AccountingService
from fastapi.encoders import jsonable_encoder
import json

engine = create_engine("postgresql://user:password@localhost:5434/business_db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run():
    db = SessionLocal()
    service = AccountingService(db)
    res = service.get_libro_compras(company_id=1)
    print(json.dumps(jsonable_encoder(res), indent=2))
    db.close()

if __name__ == "__main__":
    run()
