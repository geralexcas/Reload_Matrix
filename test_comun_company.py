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

def test_comun_company():
    """Test the reporte ingresos for a COMUN regime company"""
    db = SessionLocal()
    try:
        service = AccountingService(db)
        
        # Test company_id 22 (COMUN regime)
        with set_tenant_context(22):
            result = service.get_reporte_ingresos(company_id=22)
            
            print("Reporte de Ingresos - COMUN Regime Company:")
            print(f"Company: {result['company_name']}")
            print(f"Regimen: COMUN")
            print(f"Number of invoices: {result['totals']['num_facturas']}")
            print(f"Total ingresos operacionales: {result['totals']['total_ingresos_operacionales']}")
            print(f"Total IVA generado: {result['totals']['total_iva_generado']}")
            
            if result['entries']:
                print(f"\nFirst 3 entries:")
                for i, entry in enumerate(result['entries'][:3]):
                    print(f"  {i+1}. {entry['invoice_number']} - Base: {entry['base']} - IVA: {entry['tax_amount']} - Total: {entry['total']}")
            else:
                print("No entries found")
        
    except Exception as e:
        print(f"Error testing COMUN company: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_comun_company()
