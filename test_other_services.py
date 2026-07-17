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

def test_repair_service():
    """Test repair service for joinedload issues"""
    db = SessionLocal()
    try:
        from app.models.sql.repair import RepairOrder
        from sqlalchemy.orm import joinedload
        from sqlalchemy import and_
        
        with set_tenant_context(1):
            # Test repair orders with joinedload
            repair_orders = (
                db.query(RepairOrder)
                .options(joinedload(RepairOrder.items))
                .filter(RepairOrder.company_id == 1)
                .limit(3)
                .all()
            )
            
            print(f"Repair orders found: {len(repair_orders)}")
            for i, order in enumerate(repair_orders):
                print(f"  Order {i+1}: {order.order_number}")
                print(f"    Items loaded: {hasattr(order, 'items')}")
                if hasattr(order, 'items'):
                    print(f"    Number of items: {len(order.items) if order.items else 0}")
                    if order.items:
                        print(f"    First item: {order.items[0].description if order.items else 'N/A'}")
                    else:
                        print("    ⚠️  Items not loaded (potential joinedload issue)")
        
    except Exception as e:
        print(f"Error testing repair service: {e}")
    finally:
        db.close()

def test_purchase_service():
    """Test purchase service for joinedload issues"""
    db = SessionLocal()
    try:
        from app.models.sql.purchases import Purchase
        from sqlalchemy.orm import joinedload
        
        with set_tenant_context(1):
            # Test purchases with joinedload
            purchases = (
                db.query(Purchase)
                .options(joinedload(Purchase.items))
                .filter(Purchase.company_id == 1)
                .limit(3)
                .all()
            )
            
            print(f"\nPurchases found: {len(purchases)}")
            for i, purchase in enumerate(purchases):
                print(f"  Purchase {i+1}: {purchase.id}")
                print(f"    Items loaded: {hasattr(purchase, 'items')}")
                if hasattr(purchase, 'items'):
                    print(f"    Number of items: {len(purchase.items) if purchase.items else 0}")
                    if purchase.items:
                        print(f"    First item: {purchase.items[0].description if purchase.items else 'N/A'}")
                    else:
                        print("    ⚠️  Items not loaded (potential joinedload issue)")
        
    except Exception as e:
        print(f"Error testing purchase service: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Testing other services for joinedload issues...")
    test_repair_service()
    test_purchase_service()
    print("\nTest completed.")
