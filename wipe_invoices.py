import sys
from app.core.database import SessionLocal
from app.models.sql.invoicing import Invoice, InvoiceResolution

db = SessionLocal()
try:
    db.query(Invoice).delete()
    db.query(InvoiceResolution).delete()
    db.commit()
    print("Invoices and resolutions deleted successfully")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
