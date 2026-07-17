#!/usr/bin/env python3

import sys
import os
sys.path.append('./backend')
os.environ['ENVIRONMENT'] = 'development'

from app.core.database import SessionLocal
from app.services.repair_service import RepairService
from app.services.purchase_service import PurchaseService
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

def test_repair_service_fixed():
    """Test repair service methods after fix"""
    db = SessionLocal()
    try:
        service = RepairService(db)
        
        with set_tenant_context(1):
            # Test get_repair_orders
            orders = service.get_repair_orders(company_id=1, limit=3)
            
            print(f"Repair orders from service: {len(orders)}")
            for i, order in enumerate(orders):
                print(f"  Order {i+1}: {order.order_number}")
                print(f"    Items loaded: {hasattr(order, 'items')}")
                if hasattr(order, 'items'):
                    # Access items to trigger lazy loading
                    item_count = len(order.items) if order.items else 0
                    print(f"    Number of items: {item_count}")
                    if item_count > 0:
                        print(f"    ✅ Items loaded correctly: {order.items[0].description}")
                    else:
                        print(f"    ⚠️  No items found for this order")
                else:
                    print("    ❌ No items attribute")
        
    except Exception as e:
        print(f"Error testing repair service: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def test_purchase_service_fixed():
    """Test purchase service methods after fix"""
    db = SessionLocal()
    try:
        service = PurchaseService(db)
        
        with set_tenant_context(1):
            # Test get_purchases
            purchases = service.get_purchases(company_id=1, limit=3)
            
            print(f"\nPurchases from service: {len(purchases)}")
            for i, purchase in enumerate(purchases):
                print(f"  Purchase {i+1}: {purchase.id}")
                print(f"    Items loaded: {hasattr(purchase, 'items')}")
                if hasattr(purchase, 'items'):
                    # Access items to trigger lazy loading
                    item_count = len(purchase.items) if purchase.items else 0
                    print(f"    Number of items: {item_count}")
                    if item_count > 0:
                        print(f"    ✅ Items loaded correctly: {purchase.items[0].description}")
                    else:
                        print(f"    ⚠️  No items found for this purchase")
                else:
                    print("    ❌ No items attribute")
        
    except Exception as e:
        print(f"Error testing purchase service: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("Testing services after joinedload fixes...")
    test_repair_service_fixed()
    test_purchase_service_fixed()
    print("\nTest completed.")
