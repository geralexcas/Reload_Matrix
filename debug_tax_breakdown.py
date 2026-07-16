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

def debug_tax_breakdown():
    """Debug the tax breakdown method step by step"""
    db = SessionLocal()
    try:
        service = AccountingService(db)
        
        # Set tenant context to company_id 1
        with set_tenant_context(1):
            from app.models.sql.invoicing import Invoice
            
            # Get invoice 2
            invoice = db.query(Invoice).filter(Invoice.id == 2).first()
            
            if invoice:
                print(f"Invoice: {invoice.invoice_number}")
                print(f"Total amount: {invoice.total_amount}")
                print(f"Has items attribute: {hasattr(invoice, 'items')}")
                print(f"Items: {invoice.items if hasattr(invoice, 'items') else 'N/A'}")
                
                if hasattr(invoice, 'items') and invoice.items:
                    print(f"Number of items: {len(invoice.items)}")
                    
                    # Manually replicate the tax breakdown logic
                    base_iva_19 = Decimal("0.00")
                    iva_19 = Decimal("0.00")
                    base_iva_5 = Decimal("0.00")
                    iva_5 = Decimal("0.00")
                    base_no_iva = Decimal("0.00")
                    
                    for i, item in enumerate(invoice.items):
                        print(f"\nItem {i+1}:")
                        print(f"  Description: {item.description[:50]}...")
                        print(f"  Line total: {item.line_total}")
                        print(f"  Tax rate: {item.tax_rate}")
                        print(f"  Tax amount: {item.tax_amount}")
                        
                        item_tax_amount = item.tax_amount if item.tax_amount is not None else Decimal("0.00")
                        line_base = item.line_total - item_tax_amount
                        if line_base < 0:
                            line_base = Decimal("0.00")
                        
                        tax_rate_val = item.tax_rate if item.tax_rate is not None else Decimal("0.00")
                        tax_rate = service._parse_tax_rate(tax_rate_val)
                        
                        print(f"  Parsed tax rate: {tax_rate}")
                        print(f"  Item tax amount: {item_tax_amount}")
                        print(f"  Line base: {line_base}")
                        
                        # Check the condition
                        if item_tax_amount == 0 and tax_rate > 0:
                            print(f"  ⚠️  Condition met: tax_amount=0 and tax_rate>0")
                            item_tax_amount = line_base * tax_rate
                            line_base = item.line_total - item_tax_amount
                            if line_base < 0:
                                line_base = Decimal("0.00")
                            print(f"  Recalculated tax amount: {item_tax_amount}")
                            print(f"  Recalculated line base: {line_base}")
                        
                        if service._is_approx_equal(tax_rate, Decimal("0.19")):
                            print(f"  → Adding to IVA 19%")
                            base_iva_19 += line_base
                            iva_19 += item_tax_amount
                        elif service._is_approx_equal(tax_rate, Decimal("0.05")):
                            print(f"  → Adding to IVA 5%")
                            base_iva_5 += line_base
                            iva_5 += item_tax_amount
                        else:
                            print(f"  → Adding to no IVA")
                            base_no_iva += item.line_total
                    
                    print(f"\nFinal calculation:")
                    print(f"  Base IVA 19: {base_iva_19}")
                    print(f"  IVA 19: {iva_19}")
                    print(f"  Base IVA 5: {base_iva_5}")
                    print(f"  IVA 5: {iva_5}")
                    print(f"  Base no IVA: {base_no_iva}")
                    
                    # Call the actual method
                    taxes = service._get_invoice_tax_breakdown(invoice)
                    print(f"\nActual method result:")
                    print(f"  Base IVA 19: {taxes['base_iva_19']}")
                    print(f"  IVA 19: {taxes['iva_19']}")
                    print(f"  Base IVA 5: {taxes['base_iva_5']}")
                    print(f"  IVA 5: {taxes['iva_5']}")
                    print(f"  Base no IVA: {taxes['base_no_iva']}")
                else:
                    print("No items found or items not loaded")
            else:
                print("Invoice not found")
        
    except Exception as e:
        print(f"Error debugging tax breakdown: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_tax_breakdown()
