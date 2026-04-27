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


class RepairOrder(Base):
    __tablename__ = "repair_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    partner_id = Column(Integer, ForeignKey("partners.id"))
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    issue_date = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expected_delivery_date = Column(DateTime(timezone=True), nullable=True)
    actual_delivery_date = Column(DateTime(timezone=True), nullable=True)
    problem_description = Column(String(1000))
    diagnosis = Column(String(1000))
    service_notes = Column(String(2000))
    status = Column(
        Enum(
            "RECEIVED",
            "DIAGNOSIS",
            "APPROVED",
            "IN_REPAIR",
            "WAITING_PARTS",
            "READY",
            "DELIVERED",
            "CANCELLED",
            name="repair_order_status",
        ),
        default="RECEIVED",
    )
    warranty_applied = Column(Boolean, default=False)
    total_labor_cost = Column(Numeric(15, 2), default=0.00)
    total_parts_cost = Column(Numeric(15, 2), default=0.00)
    total_amount = Column(Numeric(15, 2), default=0.00)
    currency = Column(String(3), default="COP")
    cufe = Column(String(100), unique=True, index=True)
    xml_ubl = Column(String)
    estado_dian = Column(
        Enum("BORRADOR", "ENVIADO", "ACEPTADO", "RECHAZADO", name="invoice_dian_state"),
        default="BORRADOR",
    )
    motivo_rechazo = Column(String)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company")
    partner = relationship("Partner")
    technician = relationship("User")
    invoice = relationship("Invoice")
    items = relationship(
        "RepairItem", back_populates="repair_order", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<RepairOrder(id={self.id}, number='{self.order_number}', status='{self.status}', total={self.total_amount})>"


class RepairItem(Base):
    __tablename__ = "repair_items"

    id = Column(Integer, primary_key=True, index=True)
    repair_order_id = Column(Integer, ForeignKey("repair_orders.id"))
    description = Column(String(255), nullable=False)
    serial_number = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    brand = Column(String(100), nullable=True)
    issue_reported = Column(String(500))
    quantity = Column(Integer, default=1)
    unit_cost = Column(Numeric(15, 2), default=0.00)
    discount = Column(Numeric(15, 2), default=0.00)
    tax_rate = Column(Numeric(5, 2), default=0.00)
    tax_amount = Column(Numeric(15, 2), default=0.00)
    line_total = Column(Numeric(15, 2), default=0.00)
    warranty_status = Column(
        Enum(
            "NO_WARRANTY", "IN_WARRANTY", "WARRANTY_VOID", name="warranty_status_types"
        ),
        default="NO_WARRANTY",
    )
    warranty_days = Column(Integer, nullable=True)  # Días de garantía
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)

    repair_order = relationship("RepairOrder", back_populates="items")

    def __repr__(self):
        return f"<RepairItem(id={self.id}, repair_order_id={self.repair_order_id}, description='{self.description}')>"


class Warranty(Base):
    __tablename__ = "warranties"

    id = Column(Integer, primary_key=True, index=True)
    repair_order_id = Column(Integer, ForeignKey("repair_orders.id"), nullable=False)
    repair_item_id = Column(Integer, ForeignKey("repair_items.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    warranty_type = Column(
        Enum("MANUFACTURER", "SERVICE", "PARTS", name="warranty_types"),
        nullable=False,
        default="SERVICE",
    )
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(
        Enum("ACTIVE", "EXPIRED", "VOID", "CLAIMED", name="warranty_statuses"),
        default="ACTIVE",
    )
    description = Column(String(1000))
    terms_and_conditions = Column(Text)
    claim_date = Column(DateTime(timezone=True), nullable=True)
    claim_description = Column(String(1000), nullable=True)
    claim_resolution = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    repair_order = relationship("RepairOrder", backref="warranties")
    repair_item = relationship("RepairItem", backref="warranties")
    company = relationship("Company")

    def __repr__(self):
        return f"<Warranty(id={self.id}, type='{self.warranty_type}', status='{self.status}', end_date='{self.end_date}')>"


class Technician(Base):
    __tablename__ = "technicians"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    specialty = Column(String(200))
    is_active = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company")

    def __repr__(self):
        return f"<Technician(id={self.id}, employee_id='{self.employee_id}', name='{self.first_name} {self.last_name}')>"
