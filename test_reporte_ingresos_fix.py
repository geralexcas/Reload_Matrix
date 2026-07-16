#!/usr/bin/env python3

import sys
import os
sys.path.append('./backend')
os.environ['ENVIRONMENT'] = 'development'

from app.core.database import SessionLocal
from app.services.accounting_service import AccountingService
from app.models.sql.invoicing import Invoice
from decimal import Decimal

def test_reporte_ingresos():
    """Test the reporte ingresos with actual database data"""
    db = SessionLocal()
    try:
        service = AccountingService(db)
        
        # Test with company_id 1 (the main company)
        result = service.get_reporte_ingresos(company_id=1)
        
        print("Reporte de Ingresos Results:")
        print(f"Company: {result['company_name']}")
        print(f"NIT: {result['company_nit']}")
        print(f"Number of invoices: {result['totals']['num_facturas']}")
        print(f"Total ingresos operacionales: {result['totals']['total_ingresos_operacionales']}")
        print(f"Total IVA generado: {result['totals']['total_iva_generado']}")
        print(f"Total devoluciones: {result['totals']['total_devoluciones']}")
        print(f"Ingresos netos: {result['totals']['ingresos_netos']}")
        print(f"\nFirst 5 entries:")
        
        for i, entry in enumerate(result['entries'][:5]):
            print(f"  {i+1}. {entry['invoice_number']} - {entry['date']} - Base: {entry['base']} - IVA: {entry['tax_amount']} - Total: {entry['total']}")
        
        # Verify the fix worked
        if result['totals']['total_ingresos_operacionales'] > 0:
            print(f"\n✅ SUCCESS: The fix is working! Ingresos operacionales: {result['totals']['total_ingresos_operacionales']}")
        else:
            print(f"\n❌ FAILURE: Ingresos operacionales is still 0")
            
        if result['totals']['total_iva_generado'] > 0:
            print(f"✅ SUCCESS: IVA generado is now: {result['totals']['total_iva_generado']}")
        else:
            print(f"❌ FAILURE: IVA generado is still 0")
            
        return result
        
    except Exception as e:
        print(f"Error testing reporte ingresos: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    test_reporte_ingresos()
