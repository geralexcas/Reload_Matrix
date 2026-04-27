from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Enum as SAEnum,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class CheckRegister(Base):
    __tablename__ = "check_register"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=False)
    check_number = Column(String(30), nullable=False)
    payee = Column(String(255), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    issue_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(
        SAEnum(
            "ISSUED",
            "DELIVERED",
            "CLEARED",
            "BOUNCED",
            "VOIDED",
            name="check_status",
        ),
        nullable=False,
        default="ISSUED",
    )
    cleared_date = Column(DateTime(timezone=True), nullable=True)
    linked_transaction_id = Column(
        Integer, ForeignKey("treasury_transactions.id"), nullable=True
    )
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company")
    bank_account = relationship("BankAccount", back_populates="checks")
    linked_transaction = relationship("TreasuryTransaction")

    def __repr__(self):
        return f"<CheckRegister(id={self.id}, number='{self.check_number}', status='{self.status}')>"
