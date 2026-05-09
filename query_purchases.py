import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.sql.purchases import Purchase

engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_purchases():
    db = SessionLocal()
    purchases = db.query(Purchase).all()
    print(f"Total purchases: {len(purchases)}")
    for p in purchases:
        print(f"ID: {p.id}, Number: {p.purchase_number}, Status: {p.status}")
    db.close()

if __name__ == "__main__":
    check_purchases()
