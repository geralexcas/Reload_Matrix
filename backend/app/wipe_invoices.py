import sys
import os

# Add the /app dir to path so absolute imports work
sys.path.append("/app")

from app.core.database import SessionLocal
from app.models.sql.invoicing import Invoice, InvoiceResolution, InvoiceItem

db = SessionLocal()
try:
    # Nullify repair_orders.invoice_id before deleting invoices
    from app.models.sql.repair import RepairOrder
    db.query(RepairOrder).update({"invoice_id": None}, synchronize_session=False)

    # Handle children first or use cascade
    db.query(InvoiceItem).delete(synchronize_session=False)
    db.query(Invoice).delete(synchronize_session=False)
    db.query(InvoiceResolution).delete(synchronize_session=False)
    db.commit()
    print("Invoices and resolutions deleted successfully")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
