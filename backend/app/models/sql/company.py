from sqlalchemy import Column, Integer, String, Date, Boolean, Enum, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    nit = Column(
        String(20), unique=True, nullable=False, index=True
    )  # Colombian Tax ID
    dv = Column(String(1), nullable=False)  # Verification digit
    legal_representative = Column(String(255), nullable=False)
    address = Column(String(500))
    phone = Column(String(50))
    email = Column(String(255))
    logo_url = Column(String(500))  # Path to stored logo
    regimen = Column(
        Enum("COMUN", "SIMPLE", "ESPECIAL", "NO_RESPONSABLE", name="regimen_types"), default="COMUN"
    )
    fecha_inicio_actividades = Column(Date, nullable=False)
    resolucion_facturacion = Column(String(100))  # DIAN resolution number
    slogan = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    invoice_footer_note = Column(Text, nullable=True)
    repair_footer_note = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_trial = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="company")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', nit='{self.nit}')>"
