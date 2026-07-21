from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from app.models.sql.inventory import Product
from app.models.sql import company as company_model
from app.schemas import inventory as inv_schema
from app.services.accounting_service import AccountingService
from app.services.treasury_service import TreasuryService
from app.models.sql.inventory_movement import InventoryMovement, InventoryMovementType


class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_product(
        self, product: inv_schema.ProductCreate, company_id: int, commit: bool = False
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

        from sqlalchemy.exc import IntegrityError
        
        db_product = Product(**product.model_dump(exclude={'skip_initial_stock_purchase'}), company_id=company_id)
        self.db.add(db_product)
        try:
            self.db.flush()
        except IntegrityError:
            self.db.rollback()
            raise ValueError("El SKU o código de barras ya existe.")

        # Create accounting entry or purchase if initial stock is provided
        # skip_initial_stock_purchase allows avoiding double purchase records when creating products during a purchase flow
        if db_product.stock_level > 0 and db_product.purchase_price > 0 and not getattr(product, 'skip_initial_stock_purchase', False):
            try:
                payment_method_str = "CASH"
                if product.payment_method:
                    if hasattr(product.payment_method, 'value'):
                        payment_method_str = product.payment_method.value
                    else:
                        payment_method_str = str(product.payment_method)

                if payment_method_str in ["CREDIT", "PARTIAL_CREDIT"] and not product.supplier_id:
                    raise ValueError("Se requiere un proveedor asignado para registrar stock inicial a crédito.")

                total_amount = db_product.stock_level * db_product.purchase_price

                if product.supplier_id:
                    # Create a formal Purchase record
                    from app.models.sql.purchases import Purchase, PurchaseItem
                    import time
                    purchase_num = f"SI-PUR-{int(time.time())}-{db_product.id}"
                    db_purchase = Purchase(
                        purchase_number=purchase_num,
                        partner_id=product.supplier_id,
                        subtotal=total_amount,
                        tax_amount=Decimal("0.00"),
                        total_amount=total_amount,
                        payment_method=payment_method_str,
                        status="ISSUED",
                        company_id=company_id,
                        notes="Stock inicial generado automáticamente desde inventario",
                    )
                    self.db.add(db_purchase)
                    self.db.flush()
                    db_purchase_item = PurchaseItem(
                        purchase_id=db_purchase.id,
                        product_id=db_product.id,
                        description=f"Stock inicial - {db_product.name}",
                        quantity=db_product.stock_level,
                        unit_price=db_product.purchase_price,
                        serial_number=db_product.barcode,
                        line_total=total_amount
                    )
                    self.db.add(db_purchase_item)
                    self.db.flush()

                    # Trigger purchase accounting (which handles accounts payable and inventory)
                    accounting_service = AccountingService(self.db)
                    accounting_service.create_journal_entry_from_purchase(
                        purchase_id=db_purchase.id,
                        company_id=company_id,
                        total_amount=total_amount,
                        subtotal=total_amount,
                        tax_amount=Decimal("0.00"),
                        partner_id=product.supplier_id,
                        payment_method=payment_method_str
                    )

                    # Withdraw from treasury if paid
                    if payment_method_str not in ["CREDIT"]:
                        treasury_service = TreasuryService(self.db)
                        account_type = "CASH" if payment_method_str == "CASH" else "BANK"
                        
                        accounts = treasury_service.get_cash_accounts(company_id) if account_type == "CASH" else treasury_service.get_bank_accounts(company_id)
                        
                        if accounts:
                            treasury_service.withdraw(
                                account_type=account_type,
                                account_id=accounts[0].id,
                                amount=total_amount,
                                description=f"Pago stock inicial - {db_product.name}",
                                reference=f"PUR-{db_purchase.id:06d}",
                                company_id=company_id,
                                skip_journal_entry=True
                            )
                else:
                    # Legacy: No supplier provided, but payment method is NOT credit. 
                    # Use the journal entry approach so it doesn't leave phantom debt.
                    accounting_service = AccountingService(self.db)
                    accounting_service.create_journal_entry_for_initial_stock(
                        product_id=db_product.id,
                        product_name=db_product.name,
                        company_id=company_id,
                        total_amount=total_amount,
                        payment_method=payment_method_str
                    )
                    
                    if payment_method_str not in ["CREDIT"]:
                        treasury_service = TreasuryService(self.db)
                        account_type = "CASH" if payment_method_str == "CASH" else "BANK"
                        accounts = treasury_service.get_cash_accounts(company_id) if account_type == "CASH" else treasury_service.get_bank_accounts(company_id)
                        
                        if accounts:
                            treasury_service.withdraw(
                                account_type=account_type,
                                account_id=accounts[0].id,
                                amount=total_amount,
                                description=f"Stock inicial - {db_product.name}",
                                reference=f"SI-{db_product.id:06d}",
                                company_id=company_id,
                                skip_journal_entry=True
                            )

            except ValueError as ve:
                self.db.rollback()
                if str(ve) == "Insufficient balance":
                    raise ValueError(
                        f"No hay saldo suficiente en tesorería para pagar el stock inicial en {payment_method_str}. "
                        "Por favor, asigne un proveedor y seleccione la forma de pago 'Crédito' o registre fondos primero."
                    )
                raise ve
            except Exception as e:
                self.db.rollback()
                import logging
                logging.error(f"Error creating accounting/treasury entry: {e}")
                raise e

        if commit:
            self.db.commit()
            self.db.refresh(db_product)
        return db_product

    def bulk_create_products(
        self, bulk_data: inv_schema.ProductBulkCreate, company_id: int, commit: bool = False
    ) -> List[Product]:
        """Create multiple products at once, each with a unique barcode and SKU."""
        created_products = []
        
        # Base data for all products (excluding barcodes, barcode, sku and stock_level)
        base_data = bulk_data.model_dump(exclude={'barcodes', 'barcode', 'sku', 'stock_level'})
        base_sku = bulk_data.sku
        
        for barcode in bulk_data.barcodes:
            # Generate a unique SKU by appending the barcode/serial
            # SKU column is String(50), so we might need to truncate
            # We use up to 49 characters to leave room for the dash
            max_base_len = 49 - len(barcode)
            unique_sku = f"{base_sku[:max_base_len]}-{barcode}"
            
            # Create ProductCreate schema for this specific item
            item_data = inv_schema.ProductCreate(
                **base_data,
                sku=unique_sku,
                barcode=barcode,
                stock_level=Decimal("1.00") # Serialized items are created unit by unit
            )
            # Ensure skip_initial_stock_purchase is set correctly without double-passing
            item_data.skip_initial_stock_purchase = getattr(bulk_data, 'skip_initial_stock_purchase', False)
            
            try:
                db_product = self.create_product(item_data, company_id, commit=False)
                created_products.append(db_product)
            except ValueError as e:
                # If one fails (e.g. duplicate barcode/SKU), we rollback EVERYTHING
                self.db.rollback()
                raise e
                
        self.db.flush()
        if commit:
            self.db.commit()
        for p in created_products:
            self.db.refresh(p)
        return created_products

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
        self, product_id: int, product: inv_schema.ProductCreate, company_id: int, commit: bool = False
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

            for key, value in product.model_dump(exclude={'skip_initial_stock_purchase', 'stock_level', 'purchase_price'}).items():
                setattr(db_product, key, value)
            self.db.flush()
            if commit:
                self.db.commit()
            self.db.refresh(db_product)
        return db_product

    def delete_product(self, product_id: int, company_id: int, commit: bool = False) -> bool:
        db_product = self.get_product_by_id(product_id, company_id)
        if db_product:
            from sqlalchemy.exc import IntegrityError
            try:
                self.db.delete(db_product)
                if commit:
                    self.db.commit()
                return True
            except IntegrityError:
                self.db.rollback()
                db_product.is_active = False
                if commit:
                    self.db.commit()
                raise ValueError("El producto tiene movimientos históricos registrados (facturas, compras o asientos). Por seguridad contable, se ha marcado como INACTIVO en lugar de eliminarse.")
        return False

    def adjust_stock_level(
        self, product_id: int, adjustment: int, company_id: int, commit: bool = False
    ) -> Optional[Product]:
        """Adjust stock level by a positive or negative amount"""
        db_product = self.db.query(Product).filter(
            Product.id == product_id, Product.company_id == company_id
        ).with_for_update().first()
        if not db_product:
            raise ValueError(f"Producto con ID {product_id} no encontrado")

        decimal_adjustment = Decimal(str(adjustment))
        new_stock_level = db_product.stock_level + decimal_adjustment
        if new_stock_level < 0:
            raise ValueError("Stock level cannot be negative")

        db_product.stock_level = new_stock_level
        # Register inventory movement (Kardex) for adjustment
        movement = InventoryMovement(
            product_id=product_id,
            company_id=company_id,
            movement_type=InventoryMovementType.ADJUST,
            quantity=Decimal(str(adjustment)),
            reference=None,
            reference_id=None,
            reference_type=None,
        )
        self.db.add(movement)
        self.db.flush()
        if commit:
            self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def deduct_stock(
        self, product_id: int, quantity: Decimal, company_id: int, commit: bool = False
    ) -> Optional[Product]:
        """Deduct stock for a product. Returns the updated product or raises error."""
        from decimal import Decimal

        if quantity <= 0:
            raise ValueError(f"Quantity must be positive, got {quantity}")

        db_product = self.db.query(Product).filter(
            Product.id == product_id, Product.company_id == company_id
        ).with_for_update().first()
        if not db_product:
            raise ValueError(f"Producto con ID {product_id} no encontrado")

        if db_product.stock_level < Decimal(str(quantity)):
            raise ValueError(
                f"¡Ups! Parece que no hay suficiente stock para el producto '{db_product.name}'. "
                f"Actualmente tienes {db_product.stock_level} unidades disponibles, "
                f"pero estás intentando facturar {quantity}."
            )

        db_product.stock_level -= Decimal(str(quantity))
        # Register inventory movement (Kardex) for deduction
        movement = InventoryMovement(
            product_id=product_id,
            company_id=company_id,
            movement_type=InventoryMovementType.DEDUCT,
            quantity=Decimal(str(quantity)),
            reference=None,
            reference_id=None,
            reference_type=None,
        )
        self.db.add(movement)
        if commit:
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
        return db_product.stock_level >= Decimal(str(quantity))

    def add_stock(
        self,
        product_id: int,
        quantity: Decimal,
        company_id: int,
        reference: str = None,
        reference_id: int = None,
        reference_type: str = None,
        unit_price: Optional[Decimal] = None,
        commit: bool = False,
    ) -> Product:
        """Add stock for a product (e.g., from a purchase)."""
        db_product = self.db.query(Product).filter(Product.id == product_id, Product.company_id == company_id).with_for_update().first()
        if not db_product:
            raise ValueError(f"Product with id {product_id} not found")

        # Capture current stock BEFORE update for weighted average calculation
        previous_stock = db_product.stock_level

        # Update stock level
        db_product.stock_level = previous_stock + Decimal(str(quantity))

        # Weighted average cost if unit_price provided
        if unit_price is not None:
            current_price = db_product.purchase_price or Decimal("0.00")
            total_existing = previous_stock * current_price
            total_new = Decimal(str(quantity)) * unit_price
            new_total_stock = previous_stock + Decimal(str(quantity))
            if new_total_stock > 0:
                new_average = (total_existing + total_new) / new_total_stock
                db_product.purchase_price = new_average.quantize(Decimal("0.01"))
            else:
                db_product.purchase_price = unit_price

            # Record price history
            from app.models.sql.product_price_history import ProductPriceHistory
            price_hist = ProductPriceHistory(
                product_id=product_id,
                company_id=company_id,
                price=unit_price,
            )
            self.db.add(price_hist)

        # Register inventory movement (Kardex)
        movement = InventoryMovement(
            product_id=product_id,
            company_id=company_id,
            movement_type=InventoryMovementType.ADD,
            quantity=Decimal(str(quantity)),
            reference=reference,
            reference_id=reference_id,
            reference_type=reference_type,
        )
        self.db.add(movement)

        if commit:
            self.db.commit()
            self.db.refresh(db_product)
        return db_product
