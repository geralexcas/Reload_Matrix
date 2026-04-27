from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Boolean,
    Enum as SAEnum,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class BankReconciliation(Base):
    __tablename__ = "bank_reconciliations"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=False)
    statement_date = Column(DateTime(timezone=True), nullable=False)
    statement_balance = Column(Numeric(15, 2), nullable=False)
    system_balance = Column(Numeric(15, 2), nullable=False)
    outstanding_deposits = Column(Numeric(15, 2), default=0.00)
    outstanding_checks = Column(Numeric(15, 2), default=0.00)
    bank_fees_not_recorded = Column(Numeric(15, 2), default=0.00)
    interest_not_recorded = Column(Numeric(15, 2), default=0.00)
    adjusted_balance = Column(Numeric(15, 2))
    is_balanced = Column(Boolean, default=False)
    status = Column(
        SAEnum("IN_PROGRESS", "COMPLETED", name="reconciliation_status"),
        nullable=False,
        default="IN_PROGRESS",
    )
    reconciled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reconciled_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company")
    bank_account = relationship("BankAccount")
    reconciled_user = relationship("User")
    lines = relationship(
        "ReconciliationLine",
        back_populates="reconciliation",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<BankReconciliation(id={self.id}, bank_account_id={self.bank_account_id}, status='{self.status}')>"
