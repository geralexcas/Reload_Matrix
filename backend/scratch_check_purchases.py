import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.abspath("backend"))

from app.core.database import SessionLocal
from app.models.sql.purchases import Purchase
from app.models.sql.invoicing import Invoice
from sqlalchemy.orm import joinedload

def check_purchases():
    db = SessionLocal()
    try:
        purchases = db.query(Purchase).all()
        print(f"Total Purchases: {len(purchases)}")
        for p in purchases:
            print(f" - Purchase ID: {p.id}, Company ID: {p.company_id}, Date: {p.purchase_date}, Number: {p.purchase_number}")
            
        invoices = db.query(Invoice).filter(Invoice.invoice_type == "PURCHASE").all()
        print(f"Total Purchase Invoices: {len(invoices)}")
        for i in invoices:
            print(f" - Invoice ID: {i.id}, Company ID: {i.company_id}, Date: {i.issue_date}, Number: {i.invoice_number}")
    finally:
        db.close()

if __name__ == "__main__":
    check_purchases()
