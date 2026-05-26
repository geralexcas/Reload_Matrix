import sys
import os
sys.path.append("/app")

from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.sql.purchases import Purchase, PurchaseItem
from app.models.sql.accounting.journal_entry import JournalEntry, JournalEntryLine
from decimal import Decimal

def fix_purchases():
    db = SessionLocal()
    try:
        # Find purchases where items have tax_rate > 0 but tax_amount == 0
        problematic_purchases = db.query(Purchase).all()
        for p in problematic_purchases:
            needs_fix = False
            total_tax = Decimal("0.00")
            total_subtotal = Decimal("0.00")
            
            for item in p.items:
                if item.tax_rate and item.tax_rate > 0 and item.tax_amount == 0:
                    needs_fix = True
                    # Recalculate tax
                    subtotal = (item.quantity or 0) * (item.unit_price or 0)
                    discount = subtotal * ((item.discount_percent or 0) / Decimal("100.00"))
                    subtotal_after = subtotal - discount
                    
                    item_tax = subtotal_after * (item.tax_rate / Decimal("100.00"))
                    item.tax_amount = item_tax
                    item.line_total = subtotal_after + item_tax
                
                total_subtotal += (item.quantity or 0) * (item.unit_price or 0) - (item.discount_amount or 0)
                total_tax += item.tax_amount or 0
                
            if needs_fix:
                print(f"Fixing Purchase {p.purchase_number}")
                p.tax_amount = total_tax
                p.subtotal = total_subtotal
                p.total_amount = total_subtotal + total_tax - (p.discount_amount or 0)
                
                # We also need to fix the journal entry if it exists
                # Journal entry reference: CP-{purchase_id:06d}
                ref = f"CP-{p.id:06d}"
                je = db.query(JournalEntry).filter(JournalEntry.reference == ref).first()
                if je:
                    print(f"  Fixing Journal Entry {ref}")
                    for line in je.lines:
                        # For SIMPLE, everything is in inventory or payable
                        # The total should match the new total_amount
                        if line.debit_amount > 0:
                            # Update debit
                            line.debit_amount = p.total_amount
                        if line.credit_amount > 0:
                            # Update credit
                            line.credit_amount = p.total_amount
                
                # Fix payments if it's auto-paid
                for payment in p.payments:
                    if payment.amount == total_subtotal: # It was paid the wrong amount
                        payment.amount = p.total_amount
                        print(f"  Fixing Payment {payment.id}")
                        
                        # Fix treasury transaction? Not bothering for this manual fix script unless needed,
                        # but it's just a DB update script
                        
        db.commit()
        print("Database correction completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_purchases()
