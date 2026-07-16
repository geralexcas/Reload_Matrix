#!/usr/bin/env python3

import sys
sys.path.append('./backend')

from decimal import Decimal
from datetime import datetime

# Mock classes to test the logic
class MockInvoiceItem:
    def __init__(self, line_total, tax_rate, tax_amount=None):
        self.line_total = Decimal(str(line_total))
        self.tax_rate = Decimal(str(tax_rate))
        self.tax_amount = Decimal(str(tax_amount)) if tax_amount is not None else Decimal("0.00")

class MockInvoice:
    def __init__(self, items):
        self.items = items

def _parse_tax_rate(tax_rate_val):
    """Convert tax rate to decimal for comparison"""
    return Decimal(str(tax_rate_val)) / Decimal("100")

def _is_approx_equal(a, b, tolerance=Decimal("0.001")):
    """Check if two decimals are approximately equal"""
    return abs(a - b) < tolerance

def _get_invoice_tax_breakdown_fixed(invoice):
    """
    Fixed version of the tax breakdown method
    """
    base_iva_19 = Decimal("0.00")
    iva_19 = Decimal("0.00")
    base_iva_5 = Decimal("0.00")
    iva_5 = Decimal("0.00")
    base_no_iva = Decimal("0.00")

    if hasattr(invoice, "items") and invoice.items:
        for item in invoice.items:
            item_tax_amount = item.tax_amount if item.tax_amount is not None else Decimal("0.00")
            line_base = item.line_total - item_tax_amount
            if line_base < 0:
                line_base = Decimal("0.00")

            tax_rate_val = item.tax_rate if item.tax_rate is not None else Decimal("0.00")
            tax_rate = _parse_tax_rate(tax_rate_val)

            # If tax_amount is 0 but tax_rate is not 0, calculate tax from line_total
            if item_tax_amount == 0 and tax_rate > 0:
                # Calculate tax amount from line_total and tax_rate
                item_tax_amount = line_base * tax_rate
                line_base = item.line_total - item_tax_amount
                if line_base < 0:
                    line_base = Decimal("0.00")

            if _is_approx_equal(tax_rate, Decimal("0.19")):
                base_iva_19 += line_base
                iva_19 += item_tax_amount
            elif _is_approx_equal(tax_rate, Decimal("0.05")):
                base_iva_5 += line_base
                iva_5 += item_tax_amount
            else:
                base_no_iva += item.line_total

    total_iva = iva_19 + iva_5

    return {
        "base_iva_19": base_iva_19,
        "iva_19": iva_19,
        "base_iva_5": base_iva_5,
        "iva_5": iva_5,
        "base_no_iva": base_no_iva,
        "total_iva": total_iva,
    }

# Test cases
print("Testing tax breakdown fix...")

# Test case 1: Item with 19% tax rate but 0 tax_amount (the problematic case)
item1 = MockInvoiceItem(line_total=100000, tax_rate=19, tax_amount=0)
invoice1 = MockInvoice([item1])
result1 = _get_invoice_tax_breakdown_fixed(invoice1)
print(f"Test 1 - Item with 19% rate, 0 tax_amount:")
print(f"  Base IVA 19: {result1['base_iva_19']}")
print(f"  IVA 19: {result1['iva_19']}")
print(f"  Base no IVA: {result1['base_no_iva']}")
print(f"  Total IVA: {result1['total_iva']}")
print()

# Test case 2: Item with 0% tax rate
item2 = MockInvoiceItem(line_total=50000, tax_rate=0, tax_amount=0)
invoice2 = MockInvoice([item2])
result2 = _get_invoice_tax_breakdown_fixed(invoice2)
print(f"Test 2 - Item with 0% rate:")
print(f"  Base IVA 19: {result2['base_iva_19']}")
print(f"  Base no IVA: {result2['base_no_iva']}")
print(f"  Total IVA: {result2['total_iva']}")
print()

# Test case 3: Mixed items
items3 = [
    MockInvoiceItem(line_total=100000, tax_rate=19, tax_amount=0),  # Should calculate 19% IVA
    MockInvoiceItem(line_total=50000, tax_rate=0, tax_amount=0),    # No IVA
    MockInvoiceItem(line_total=200000, tax_rate=19, tax_amount=0),  # Should calculate 19% IVA
]
invoice3 = MockInvoice(items3)
result3 = _get_invoice_tax_breakdown_fixed(invoice3)
print(f"Test 3 - Mixed items:")
print(f"  Base IVA 19: {result3['base_iva_19']}")
print(f"  IVA 19: {result3['iva_19']}")
print(f"  Base no IVA: {result3['base_no_iva']}")
print(f"  Total IVA: {result3['total_iva']}")
print()

print("All tests completed!")
