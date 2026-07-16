#!/usr/bin/env python3

import sys
import os
sys.path.append('./backend')
os.environ['ENVIRONMENT'] = 'development'

from app.core.database import SessionLocal
from app.services.accounting_service import AccountingService
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

def debug_reporte_query():
    """Debug the exact query used in reporte ingresos"""
    db = SessionLocal()
    try:
        service = AccountingService(db)
        
        # Set tenant context to company_id 1
        with set_tenant_context(1):
            from app.models.sql.invoicing import Invoice
            from sqlalchemy.orm import joinedload
            from sqlalchemy import and_
            
            # Replicate the exact query from get_reporte_ingresos
            date_filter = [Invoice.invoice_type == "SALE", Invoice.company_id == 1]
            
            invoices = (
                db.query(Invoice)
                .options(joinedload(Invoice.partner), joinedload(Invoice.items))
                .filter(and_(*date_filter))
                .order_by(Invoice.issue_date)
                .limit(3)
                .all()
            )
            
            print(f"Query returned {len(invoices)} invoices")
            
            # Remove duplicates (as in the service)
            invoices = list({inv.id: inv for inv in invoices}.values())
            print(f"After removing duplicates: {len(invoices)}")
            
            for i, inv in enumerate(invoices):
                if inv.status == "CANCELLED":
                    print(f"\nInvoice {i+1}: {inv.invoice_number} - CANCELLED")
                    continue
                    
                print(f"\nInvoice {i+1}: {inv.invoice_number}")
                print(f"  Status: {inv.status}")
                print(f"  Total amount: {inv.total_amount}")
                print(f"  Has items: {hasattr(inv, 'items')}")
                
                if hasattr(inv, 'items'):
                    print(f"  Items loaded: {inv.items is not None}")
                    print(f"  Number of items: {len(inv.items) if inv.items else 0}")
                    
                    if inv.items:
                        # Get tax breakdown
                        taxes = service._get_invoice_tax_breakdown(inv)
                        base = taxes["base_iva_19"] + taxes["base_iva_5"] + taxes["base_no_iva"]
                        
                        print(f"  Tax breakdown:")
                        print(f"    Base IVA 19: {taxes['base_iva_19']}")
                        print(f"    Base IVA 5: {taxes['base_iva_5']}")
                        print(f"    Base no IVA: {taxes['base_no_iva']}")
                        print(f"    Total base: {base}")
                        print(f"    Total IVA: {taxes['total_iva']}")
                    else:
                        print("  Items not loaded!")
                else:
                    print("  No items attribute!")
        
    except Exception as e:
        print(f"Error debugging reporte query: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_reporte_query()
