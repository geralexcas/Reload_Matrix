from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    Float,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class CreditDebitNote(Base):
    __tablename__ = "credit_debit_notes"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    original_invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    note_type = Column(
        Enum("CREDIT", "DEBIT", name="note_types"),
        nullable=False,
    )
    reason = Column(String(500), nullable=False)
    amount = Column(Float, nullable=False)
    note_number = Column(String(50), nullable=False, unique=True)
    cufe = Column(String(128), nullable=True)
    xml_ubl = Column(Text, nullable=True)
    estado_dian = Column(
        Enum("BORRADOR", "ENVIADO", "ACEPTADO", "RECHAZADO", name="note_dian_status"),
        default="BORRADOR",
    )
    fecha_envio_dian = Column(DateTime(timezone=True), nullable=True)
    motivo_rechazo = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company")
    original_invoice = relationship("Invoice")

    model_config = {"from_attributes": True}
