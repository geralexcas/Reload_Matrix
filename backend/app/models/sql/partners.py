from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    Float,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Partner(Base):
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True)
    nit = Column(String(20), index=True, nullable=True)  # Colombian Tax ID
    dv = Column(String(1), nullable=True)  # Verification digit
    name = Column(String(255), nullable=False)
    partner_type = Column(
        Enum("SUPPLIER", "CUSTOMER", "BOTH", name="partner_types"),
        nullable=False,
        default="CUSTOMER",
    )
    responsibility_fiscal = Column(
        Enum(
            "RESPONSABLE IVA",
            "NO RESPONSABLE",
            "AGENTE RETENEDOR",
            name="responsibility_fiscal_types",
        ),
        nullable=True,
    )
    address = Column(String(500))
    phone = Column(String(50))
    email = Column(String(255))
    contact_person = Column(String(255))
    credit_limit = Column(Float, nullable=True)  # Límite de crédito en COP
    is_active = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    company = relationship("Company")

    def __repr__(self):
        return f"<Partner(id={self.id}, nit='{self.nit}', name='{self.name}', type='{self.partner_type}', responsibility_fiscal='{self.responsibility_fiscal}')>"
