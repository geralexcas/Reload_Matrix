from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from app.models.sql.inventory import Product
from app.models.sql import company as company_model
from app.schemas import inventory as inv_schema
from app.services.accounting_service import AccountingService
from app.services.treasury_service import TreasuryService


class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_product(
        self, product: inv_schema.ProductCreate, company_id: int
    ) -> Product:
        # Validate barcode uniqueness if provided
        if product.barcode:
            existing_product = (
                self.db.query(Product)
                .filter(
                    Product.barcode == product.barcode,
                    Product.company_id == company_id,
                )
                .first()
            )
            if existing_product:
                raise ValueError("Product with this barcode already exists")

        db_product = Product(**product.model_dump(), company_id=company_id)
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)

        # Create accounting entry if initial stock is provided
        if db_product.stock_level > 0 and db_product.purchase_price > 0:
            try:
                accounting_service = AccountingService(self.db)
                
                # Get payment method as string
                payment_method_str = "CASH"
                if product.payment_method:
                    if hasattr(product.payment_method, 'value'):
                        payment_method_str = product.payment_method.value
                    else:
                        payment_method_str = str(product.payment_method)
                
                accounting_service.create_journal_entry_for_initial_stock(
                    product_id=db_product.id,
                    product_name=db_product.name,
                    company_id=company_id,
                    total_amount=db_product.stock_level * db_product.purchase_price,
                    payment_method=payment_method_str
                )
                
                # Create treasury transaction if not CREDIT
                if payment_method_str not in ["CREDIT"]:
                    treasury_service = TreasuryService(self.db)
                    account_type = "CASH" if payment_method_str == "CASH" else "BANK"
                    total_amount = db_product.stock_level * db_product.purchase_price
                    
                    if account_type == "CASH":
                        accounts = treasury_service.get_cash_accounts(company_id)
                    else:
                        accounts = treasury_service.get_bank_accounts(company_id)
                    
                    if accounts:
                        treasury_service.withdraw(
                            account_type=account_type,
                            account_id=accounts[0].id,
                            amount=total_amount,
                            description=f"Stock inicial - {db_product.name}",
                            reference=f"SI-{db_product.id:06d}",
                            company_id=company_id
                        )
                        
            except Exception as e:
                import logging
                logging.error(f"Error creating accounting/treasury entry: {e}")

        return db_product

    def get_products(
        self, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        return (
            self.db.query(Product)
            .filter(Product.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_product_by_id(self, product_id: int, company_id: int) -> Optional[Product]:
        return (
            self.db.query(Product)
            .filter(
                Product.id == product_id,
                Product.company_id == company_id,
            )
            .first()
        )

    def get_product_by_barcode(
        self, barcode: str, company_id: int
    ) -> Optional[Product]:
        """Get product by barcode for scanning functionality"""
        if not barcode:
            return None

        return (
            self.db.query(Product)
            .filter(
                Product.barcode == barcode,
                Product.company_id == company_id,
                Product.is_active == True,
            )
            .first()
        )

    def get_low_stock_products(
        self, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """Get products with stock level at or below minimum stock level"""
        return (
            self.db.query(Product)
            .filter(
                Product.company_id == company_id,
                Product.stock_level <= Product.min_stock_level,
                Product.is_active == True,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_product(
        self, product_id: int, product: inv_schema.ProductCreate, company_id: int
    ) -> Optional[Product]:
        db_product = self.get_product_by_id(product_id, company_id)
        if db_product:
            # Check barcode uniqueness if it's being changed
            if product.barcode and product.barcode != db_product.barcode:
                existing_product = (
                    self.db.query(Product)
                    .filter(
                        Product.barcode == product.barcode,
                        Product.company_id == company_id,
                        Product.id != product_id,  # Exclude current product
                    )
                    .first()
                )
                if existing_product:
                    raise ValueError("Product with this barcode already exists")

            for key, value in product.model_dump().items():
                setattr(db_product, key, value)
            self.db.commit()
            self.db.refresh(db_product)
        return db_product

    def delete_product(self, product_id: int, company_id: int) -> bool:
        db_product = self.get_product_by_id(product_id, company_id)
        if db_product:
            self.db.delete(db_product)
            self.db.commit()
            return True
        return False

    def adjust_stock_level(
        self, product_id: int, adjustment: int, company_id: int
    ) -> Optional[Product]:
        """Adjust stock level by a positive or negative amount"""
        db_product = self.get_product_by_id(product_id, company_id)
        if db_product:
            new_stock_level = float(db_product.stock_level) + adjustment
            if new_stock_level < 0:
                raise ValueError("Stock level cannot be negative")

            db_product.stock_level = new_stock_level
            self.db.commit()
            self.db.refresh(db_product)
        return db_product

    def deduct_stock(
        self, product_id: int, quantity: float, company_id: int
    ) -> Optional[Product]:
        """Deduct stock for a product. Returns the updated product or raises error."""
        from decimal import Decimal

        db_product = self.get_product_by_id(product_id, company_id)
        if not db_product:
            raise ValueError(f"Producto con ID {product_id} no encontrado")

        if db_product.stock_level < Decimal(str(quantity)):
            raise ValueError(
                f"¡Ups! Parece que no hay suficiente stock para el producto '{db_product.name}'. "
                f"Actualmente tienes {db_product.stock_level} unidades disponibles, "
                f"pero estás intentando facturar {quantity}."
            )

        db_product.stock_level -= Decimal(str(quantity))
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def check_stock_availability(
        self, product_id: int, quantity: float, company_id: int
    ) -> bool:
        """Check if there is enough stock for a product."""
        db_product = self.get_product_by_id(product_id, company_id)
        if not db_product:
            return False
        return db_product.stock_level >= quantity

    def add_stock(
        self,
        product_id: int,
        quantity: float,
        company_id: int,
        reference: str = None,
        reference_id: int = None,
        reference_type: str = None,
    ) -> Product:
        """Add stock for a product (e.g., from a purchase)."""
        db_product = self.get_product_by_id(product_id, company_id)
        if not db_product:
            raise ValueError(f"Product with id {product_id} not found")

        db_product.stock_level += Decimal(str(quantity))
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
