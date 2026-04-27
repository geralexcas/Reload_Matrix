from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Boolean,
    Enum,
    Text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    purchase_number = Column(String(50), unique=True, index=True, nullable=False)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=False)
    purchase_date = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    due_date = Column(DateTime(timezone=True))
    subtotal = Column(Numeric(15, 2), nullable=False, default=0.00)
    tax_amount = Column(Numeric(15, 2), default=0.00)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    discount_amount = Column(Numeric(15, 2), default=0.00)
    currency = Column(String(3), default="COP")

    payment_method = Column(
        Enum(
            "CASH",
            "BANK_TRANSFER",
            "CHECK",
            "CREDIT_CARD",
            "CREDIT",
            "PARTIAL_CREDIT",
            name="payment_methods",
        ),
        nullable=False,
        default="CREDIT",
    )

    status = Column(
        Enum(
            "DRAFT",
            "ISSUED",
            "PAID",
            "PARTIAL",
            "OVERDUE",
            "CANCELLED",
            name="purchase_status",
        ),
        default="DRAFT",
    )

    notes = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    company = relationship("Company")
    partner = relationship("Partner")
    creator = relationship("User")
    items = relationship(
        "PurchaseItem", back_populates="purchase", cascade="all, delete-orphan"
    )
    payments = relationship(
        "PurchasePayment", back_populates="purchase", cascade="all, delete-orphan"
    )


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0.00)
    discount_amount = Column(Numeric(15, 2), default=0.00)
    tax_rate = Column(Numeric(5, 2), default=0.00)
    tax_amount = Column(Numeric(15, 2), default=0.00)
    line_total = Column(Numeric(15, 2), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product")


class PurchasePayment(Base):
    __tablename__ = "purchase_payments"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False)
    payment_method = Column(
        Enum("CASH", "BANK_TRANSFER", "CHECK", "CREDIT_CARD", name="payment_methods"),
        nullable=False,
    )
    amount = Column(Numeric(15, 2), nullable=False)
    payment_date = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    purchase = relationship("Purchase", back_populates="payments")
    creator = relationship("User")
