from app.core.database import SessionLocal
from app.services.inventory_service import InventoryService
from app.schemas.inventory import ProductCreate

def main():
    db = SessionLocal()
    try:
        service = InventoryService(db)
        product = ProductCreate(
            sku="PROD-TEST1",
            name="Test Product",
            purchase_price=100,
            sale_price=150,
            stock_level=1,
            min_stock_level=0,
            max_stock_level=999999.99,
            payment_method="CASH"
        )
        try:
            res = service.create_product(product, company_id=1)
            print("SUCCESS", res.id)
        except Exception as e:
            print(f"FAILED WITH EXCEPTION: {type(e).__name__} - {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
