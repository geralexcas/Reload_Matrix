#!/usr/bin/env python3

import sys
import os
sys.path.append('./backend')
os.environ['ENVIRONMENT'] = 'development'

from app.core.database import SessionLocal
from app.services.accounting_service import AccountingService
from app.core.tenant_context import current_tenant_id
from contextlib import contextmanager
from decimal import Decimal

@contextmanager
def set_tenant_context(tenant_id):
    """Context manager to set tenant ID for testing"""
    token = current_tenant_id.set(tenant_id)
    try:
        yield
    finally:
        current_tenant_id.reset(token)

def debug_tax_calculation():
    """Debug the tax calculation for specific invoices"""
    db = SessionLocal()
    try:
        service = AccountingService(db)
        
        # Set tenant context to company_id 1
        with set_tenant_context(1):
            # Get a specific invoice to debug
            from app.models.sql.invoicing import Invoice
            invoice = db.query(Invoice).filter(Invoice.id == 2).first()  # INV-00000002
            
            if invoice:
                print(f"Invoice: {invoice.invoice_number}")
                print(f"Total amount: {invoice.total_amount}")
                print(f"Status: {invoice.status}")
                print(f"Items: {len(invoice.items)}")
                
                for i, item in enumerate(invoice.items):
                    print(f"\nItem {i+1}:")
                    print(f"  Description: {item.description[:50]}...")
                    print(f"  Line total: {item.line_total}")
                    print(f"  Tax rate: {item.tax_rate}%")
                    print(f"  Tax amount: {item.tax_amount}")
                    
                    # Manually calculate what should happen
                    tax_rate_decimal = Decimal(str(item.tax_rate)) / Decimal("100")
                    print(f"  Tax rate (decimal): {tax_rate_decimal}")
                    
                    if item.tax_amount == 0 and tax_rate_decimal > 0:
                        # This is the case we're trying to fix
                        line_base = item.line_total
                        calculated_tax = line_base * tax_rate_decimal
                        adjusted_base = item.line_total - calculated_tax
                        print(f"  ⚠️  Tax amount is 0 but tax rate > 0")
                        print(f"  Calculated tax: {calculated_tax}")
                        print(f"  Adjusted base: {adjusted_base}")
                    else:
                        print(f"  Tax amount is already set: {item.tax_amount}")
                
                # Test the actual method
                taxes = service._get_invoice_tax_breakdown(invoice)
                print(f"\nTax breakdown result:")
                print(f"  Base IVA 19: {taxes['base_iva_19']}")
                print(f"  IVA 19: {taxes['iva_19']}")
                print(f"  Base IVA 5: {taxes['base_iva_5']}")
                print(f"  IVA 5: {taxes['iva_5']}")
                print(f"  Base no IVA: {taxes['base_no_iva']}")
                print(f"  Total IVA: {taxes['total_iva']}")
            else:
                print("Invoice not found")
        
    except Exception as e:
        print(f"Error debugging tax calculation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_tax_calculation()
