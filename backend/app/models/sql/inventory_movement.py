from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Enum, Numeric
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class InventoryMovementType(enum.Enum):
    ADD = "ADD"
    DEDUCT = "DEDUCT"
    ADJUST = "ADJUST"

class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    movement_type = Column(Enum(InventoryMovementType), nullable=False)
    quantity = Column(Numeric(15, 2), nullable=False)
    reference = Column(String(255), nullable=True)
    reference_id = Column(Integer, nullable=True)
    reference_type = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<InventoryMovement(id={self.id}, product_id={self.product_id}, type={self.movement_type}, qty={self.quantity})>"
