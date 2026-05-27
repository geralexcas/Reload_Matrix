from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Boolean,
    Enum,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(
        String(50), unique=True, index=True, nullable=False
    )  # Número de factura
    invoice_type = Column(
        Enum("SALE", "PURCHASE", "CUENTA_COBRO", name="invoice_types"), nullable=False
    )  # VENTA, COMPRA, o CUENTA DE COBRO
    partner_id = Column(Integer, ForeignKey("partners.id"))  # Cliente o Proveedor
    issue_date = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    due_date = Column(DateTime(timezone=True))
    total_amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="COP")  # Moneda, por defecto COP
    status = Column(
        Enum("DRAFT", "ISSUED", "PAID", "CANCELLED", name="invoice_status"),
        default="DRAFT",
    )
    # Para facturación electrónica en Colombia
    cufe = Column(
        String(100), unique=True, index=True
    )  # Código Único de Factura Electrónica
    xml_ubl = Column(String)  # Contenido XML de la factura UBL 2.1
    estado_dian = Column(
        Enum("BORRADOR", "ENVIADO", "ACEPTADO", "RECHAZADO", "NO_APLICA", name="invoice_dian_state"),
        default="BORRADOR",
    )  # Estado de la factura en la DIAN
    motivo_rechazo = Column(String)  # Motivo de rechazo por la DIAN, si aplica
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    company = relationship("Company")
    partner = relationship("Partner")
    items = relationship(
        "InvoiceItem", back_populates="invoice", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', type='{self.invoice_type}', total={self.total_amount})>"


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount = Column(Numeric(15, 2), default=0.00)
    tax_rate = Column(
        Numeric(5, 2), default=0.00
    )  # Porcentaje de impuesto (ej. 19.00 para IVA)
    tax_amount = Column(Numeric(15, 2), default=0.00)
    line_total = Column(
        Numeric(15, 2), nullable=False
    )  # Cantidad * Precio unitario - Descuento + Impuesto
    # Para referencia a productos en inventario (opcional)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    # Agrupador para componentes de un equipo ensamblado (PC Armado)
    assembly_group_id = Column(String(50), nullable=True)
    # Número de serie del producto (copiado del barcode del producto serializado)
    serial_number = Column(String(255), nullable=True)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    # product = relationship("Product")  # Se definirá cuando se cree el modelo de inventario

    def __repr__(self):
        return f"<InvoiceItem(id={self.id}, invoice_id={self.invoice_id}, description='{self.description}', quantity={self.quantity})>"


class InvoiceResolution(Base):
    """
    Tracks and manages invoice numbering sequences (resoluciones de facturación).
    Allows different sequences for POS, Electronic Billing, etc.
    """
    __tablename__ = "invoice_resolutions"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # E.g., 'SALE', 'POS', 'ELECTRONIC'
    resolution_type = Column(String(50), nullable=False, default="SALE")
    
    # Official DIAN resolution number if applicable
    resolution_number = Column(String(100), nullable=True)
    
    # Prefix (e.g., 'INV-', 'FE-', 'POS-')
    prefix = Column(String(20), nullable=False, default="INV-")
    
    # Sequence boundaries and current state
    start_number = Column(Integer, nullable=False, default=1)
    end_number = Column(Integer, nullable=True)
    current_number = Column(Integer, nullable=False, default=1)
    
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company")

    def __repr__(self):
        return f"<InvoiceResolution(id={self.id}, prefix='{self.prefix}', current={self.current_number})>"
