from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class DianBillingRange(Base):
    __tablename__ = "dian_billing_ranges"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    resolution = Column(String(100), nullable=False)
    prefix = Column(String(10), nullable=False)
    from_number = Column(Integer, nullable=False)
    to_number = Column(Integer, nullable=False)
    next_number = Column(Integer, nullable=False)
    approval_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company")

    model_config = {"from_attributes": True}
