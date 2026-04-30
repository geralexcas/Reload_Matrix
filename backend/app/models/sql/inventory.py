from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(
        String(50), unique=True, index=True, nullable=False
    )  # Stock Keeping Unit
    barcode = Column(
        String(100), unique=True, index=True, nullable=True
    )  # Código de barras (EAN, UPC, etc.)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    category = Column(String(100))
    brand = Column(String(100), nullable=True)  # Marca del producto
    model = Column(String(100), nullable=True)  # Modelo del producto
    unit_of_measure = Column(String(50), default="UNIDAD")  # UNIDAD, KG, LITRO, etc.
    purchase_price = Column(Numeric(15, 2), nullable=False)  # Precio de compra
    sale_price = Column(Numeric(15, 2), nullable=False)  # Precio de venta
    stock_level = Column(Numeric(15, 2), default=0.00)  # Nivel de stock actual
    min_stock_level = Column(
        Numeric(15, 2), default=0.00
    )  # Nivel mínimo de stock para alerta
    max_stock_level = Column(Numeric(15, 2), default=999999.99)  # Nivel máximo de stock
    is_active = Column(Boolean, default=True)
    payment_method = Column(String(50), default="CASH")  # Forma de pago: CASH, BANK_TRANSFER, CREDIT
    company_id = Column(Integer, ForeignKey("companies.id"))
    supplier_id = Column(Integer, ForeignKey("partners.id"), nullable=True) # Proveedor asignado
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    company = relationship("Company")
    supplier = relationship("Partner")
    # Note: We don't have a direct relationship to invoice items here, but we can link via product_id in invoice_items

    def __repr__(self):
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}', stock={self.stock_level})>"
