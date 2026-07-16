#!/usr/bin/env python3

import sys
import os
sys.path.append('./backend')
os.environ['ENVIRONMENT'] = 'development'

from app.core.database import SessionLocal
from app.core.tenant_context import current_tenant_id
from contextlib import contextmanager

@contextmanager
def set_tenant_context(tenant_id):
    """Context manager to set tenant ID for testing"""
    token = current_tenant_id.set(tenant_id)
    try:
        yield
    finally:
        current_tenant_id.reset(token)

def test_explicit_load():
    """Test loading invoices and items explicitly"""
    db = SessionLocal()
    try:
        # Set tenant context to company_id 1
        with set_tenant_context(1):
            from app.models.sql.invoicing import Invoice, InvoiceItem
            
            # Load invoice without joinedload
            invoice = db.query(Invoice).filter(Invoice.id == 2).first()
            
            print(f"Invoice: {invoice.invoice_number}")
            print(f"Total amount: {invoice.total_amount}")
            print(f"Has items attribute: {hasattr(invoice, 'items')}")
            
            if hasattr(invoice, 'items'):
                print(f"Items loaded: {invoice.items is not None}")
                print(f"Number of items: {len(invoice.items) if invoice.items else 0}")
                
                # Try explicit query for items
                items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == 2).all()
                print(f"Explicit query for items: {len(items)}")
                
                for i, item in enumerate(items):
                    print(f"  Item {i+1}: {item.description[:50]}... - {item.line_total}")
            
    except Exception as e:
        print(f"Error testing explicit load: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_explicit_load()
