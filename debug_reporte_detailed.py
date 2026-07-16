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

def debug_reporte_detailed():
    """Debug the reporte ingresos calculation in detail"""
    db = SessionLocal()
    try:
        service = AccountingService(db)
        
        # Set tenant context to company_id 1
        with set_tenant_context(1):
            from app.models.sql.invoicing import Invoice
            from sqlalchemy.orm import joinedload
            from sqlalchemy import and_
            
            # Get first few invoices
            date_filter = [Invoice.invoice_type == "SALE", Invoice.company_id == 1]
            invoices = (
                db.query(Invoice)
                .options(joinedload(Invoice.partner), joinedload(Invoice.items))
                .filter(and_(*date_filter))
                .order_by(Invoice.issue_date)
                .limit(3)
                .all()
            )
            
            print(f"Found {len(invoices)} invoices")
            
            for i, inv in enumerate(invoices):
                if inv.status == "CANCELLED":
                    print(f"\nInvoice {i+1}: {inv.invoice_number} - CANCELLED (skipped)")
                    continue
                    
                print(f"\nInvoice {i+1}: {inv.invoice_number}")
                print(f"  Total amount: {inv.total_amount}")
                print(f"  Status: {inv.status}")
                
                # Get tax breakdown
                taxes = service._get_invoice_tax_breakdown(inv)
                print(f"  Tax breakdown:")
                print(f"    Base IVA 19: {taxes['base_iva_19']}")
                print(f"    Base IVA 5: {taxes['base_iva_5']}")
                print(f"    Base no IVA: {taxes['base_no_iva']}")
                
                base = taxes["base_iva_19"] + taxes["base_iva_5"] + taxes["base_no_iva"]
                print(f"    Total base: {base}")
                print(f"    Total IVA: {taxes['total_iva']}")
                
                # This should match the invoice total_amount
                expected_total = base + taxes['total_iva']
                print(f"    Expected total: {expected_total}")
                print(f"    Actual total: {inv.total_amount}")
                print(f"    Match: {expected_total == inv.total_amount}")
        
    except Exception as e:
        print(f"Error debugging reporte: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_reporte_detailed()
