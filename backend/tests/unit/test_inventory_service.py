import pytest
from decimal import Decimal
from app.services.inventory_service import InventoryService
from app.schemas.inventory import ProductCreate


class TestInventoryService:
    def test_create_product(self, db_session, test_company):
        service = InventoryService(db_session)
        product_data = ProductCreate(
            sku="TEST-001",
            barcode="7701234567890",
            name="Test Product",
            description="A test product",
            category="Test",
            unit_measure="UNI",
            purchase_price=Decimal("10000.00"),
            sale_price=Decimal("15000.00"),
            stock_level=Decimal("100.00"),
            min_stock=Decimal("10.00"),
            max_stock=Decimal("500.00"),
        )
        product = service.create_product(product_data, test_company.id)
        assert product.name == "Test Product"
        assert product.stock_level == Decimal("100.00")

    def test_deduct_stock_success(self, db_session, test_company):
        from decimal import Decimal

        service = InventoryService(db_session)
        product_data = ProductCreate(
            sku="TEST-002",
            name="Test Product 2",
            category="Test",
            unit_measure="UNI",
            purchase_price=Decimal("10000.00"),
            sale_price=Decimal("15000.00"),
            stock_level=Decimal("50.00"),
            min_stock=Decimal("5.00"),
            max_stock=Decimal("200.00"),
        )
        product = service.create_product(product_data, test_company.id)
        result = service.deduct_stock(product.id, 10.0, test_company.id)
        assert result.stock_level == Decimal("40.00")

    def test_deduct_stock_insufficient(self, db_session, test_company):
        from decimal import Decimal

        service = InventoryService(db_session)
        product_data = ProductCreate(
            sku="TEST-003",
            name="Test Product 3",
            category="Test",
            unit_measure="UNI",
            purchase_price=Decimal("10000.00"),
            sale_price=Decimal("15000.00"),
            stock_level=Decimal("5.00"),
            min_stock=Decimal("1.00"),
            max_stock=Decimal("100.00"),
        )
        product = service.create_product(product_data, test_company.id)
        with pytest.raises(ValueError, match="Insufficient stock"):
            service.deduct_stock(product.id, 10.0, test_company.id)

    def test_check_stock_availability(self, db_session, test_company):
        from decimal import Decimal

        service = InventoryService(db_session)
        product_data = ProductCreate(
            sku="TEST-004",
            name="Test Product 4",
            category="Test",
            unit_measure="UNI",
            purchase_price=Decimal("10000.00"),
            sale_price=Decimal("15000.00"),
            stock_level=Decimal("20.00"),
            min_stock=Decimal("5.00"),
            max_stock=Decimal("100.00"),
        )
        product = service.create_product(product_data, test_company.id)
        assert (
            service.check_stock_availability(product.id, 15.0, test_company.id) is True
        )
        assert (
            service.check_stock_availability(product.id, 25.0, test_company.id) is False
        )

    def test_adjust_stock_positive(self, db_session, test_company):
        from decimal import Decimal

        service = InventoryService(db_session)
        product_data = ProductCreate(
            sku="TEST-005",
            name="Test Product 5",
            category="Test",
            unit_measure="UNI",
            purchase_price=Decimal("10000.00"),
            sale_price=Decimal("15000.00"),
            stock_level=Decimal("50.00"),
            min_stock=Decimal("5.00"),
            max_stock=Decimal("100.00"),
        )
        product = service.create_product(product_data, test_company.id)
        result = service.adjust_stock_level(product.id, 25, test_company.id)
        assert result.stock_level == Decimal("75.00")

    def test_adjust_stock_negative(self, db_session, test_company):
        from decimal import Decimal

        service = InventoryService(db_session)
        product_data = ProductCreate(
            sku="TEST-006",
            name="Test Product 6",
            category="Test",
            unit_measure="UNI",
            purchase_price=Decimal("10000.00"),
            sale_price=Decimal("15000.00"),
            stock_level=Decimal("50.00"),
            min_stock=Decimal("5.00"),
            max_stock=Decimal("100.00"),
        )
        product = service.create_product(product_data, test_company.id)
        result = service.adjust_stock_level(product.id, -20, test_company.id)
        assert result.stock_level == Decimal("30.00")
