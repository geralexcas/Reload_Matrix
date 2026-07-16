#!/usr/bin/env python3

import sys
import os
sys.path.append('./backend')
os.environ['ENVIRONMENT'] = 'development'

from app.core.database import SessionLocal
from app.models.sql.invoicing import Invoice
from sqlalchemy.orm import joinedload
from sqlalchemy import and_

def debug_invoices():
    """Debug the invoice query"""
    db = SessionLocal()
    try:
        # Check basic invoice count
        all_invoices = db.query(Invoice).filter(Invoice.invoice_type == "SALE").all()
        print(f"Total SALE invoices: {len(all_invoices)}")
        
        # Check invoices for company_id 1
        company_invoices = db.query(Invoice).filter(
            and_(
                Invoice.invoice_type == "SALE",
                Invoice.company_id == 1
            )
        ).all()
        print(f"SALE invoices for company 1: {len(company_invoices)}")
        
        # Check non-cancelled invoices for company_id 1
        non_cancelled = [inv for inv in company_invoices if inv.status != "CANCELLED"]
        print(f"Non-cancelled SALE invoices for company 1: {len(non_cancelled)}")
        
        # Show some details
        print(f"\nFirst 5 non-cancelled invoices:")
        for i, inv in enumerate(non_cancelled[:5]):
            print(f"  {i+1}. ID: {inv.id}, Number: {inv.invoice_number}, Status: {inv.status}, Amount: {inv.total_amount}, Date: {inv.issue_date}")
            if inv.items:
                print(f"     Items: {len(inv.items)}")
                for item in inv.items[:2]:  # Show first 2 items
                    print(f"       - {item.description[:50]}... Rate: {item.tax_rate}%, Amount: {item.tax_amount}")
        
        # Test the exact query from the service
        from datetime import datetime
        date_filter = [Invoice.invoice_type == "SALE", Invoice.company_id == 1]
        
        invoices = (
            db.query(Invoice)
            .options(joinedload(Invoice.partner), joinedload(Invoice.items))
            .filter(and_(*date_filter))
            .order_by(Invoice.issue_date)
            .all()
        )
        print(f"\nQuery result count: {len(invoices)}")
        
        # Remove duplicates (as in the service)
        invoices = list({inv.id: inv for inv in invoices}.values())
        print(f"After removing duplicates: {len(invoices)}")
        
        return len(invoices)
        
    except Exception as e:
        print(f"Error debugging invoices: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    debug_invoices()
