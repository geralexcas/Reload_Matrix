from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ReconciliationLine(Base):
    __tablename__ = "reconciliation_lines"

    id = Column(Integer, primary_key=True, index=True)
    reconciliation_id = Column(
        Integer, ForeignKey("bank_reconciliations.id"), nullable=False
    )
    treasury_transaction_id = Column(
        Integer, ForeignKey("treasury_transactions.id"), nullable=True
    )
    is_matched = Column(Boolean, default=False)
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(String(500))
    statement_date = Column(DateTime(timezone=True), nullable=True)
    system_date = Column(DateTime(timezone=True), nullable=True)
    difference = Column(Numeric(15, 2), default=0.00)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    reconciliation = relationship("BankReconciliation", back_populates="lines")
    treasury_transaction = relationship("TreasuryTransaction")

    def __repr__(self):
        return f"<ReconciliationLine(id={self.id}, amount={self.amount}, matched={self.is_matched})>"
