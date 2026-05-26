from app.core.database import SessionLocal
from app.models.sql.company import Company
from app.models.sql.partners import Partner
from app.models.sql.purchases import Purchase
import sys

db = SessionLocal()
comp = db.query(Company).first()
print(f"Company: {comp.name}, Regimen: {comp.regimen}")

p = db.query(Purchase).order_by(Purchase.id.desc()).first()
if p:
    print(f"Last Purchase: ID {p.id}, Number: {p.purchase_number}, Total: {p.total_amount}, Tax: {p.tax_amount}, Subtotal: {p.subtotal}")
    partner = db.query(Partner).filter(Partner.id == p.partner_id).first()
    print(f"Supplier: {partner.name}, Is IVA responsible: {partner.is_iva_responsible if hasattr(partner, 'is_iva_responsible') else 'N/A'}, Tax Type: {partner.tax_type if hasattr(partner, 'tax_type') else 'N/A'}")
else:
    print("No purchases found.")

db.close()
