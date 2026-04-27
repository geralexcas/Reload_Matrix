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


class TreasuryTransaction(Base):
    __tablename__ = "treasury_transactions"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    account_type = Column(
        SAEnum("BANK", "CASH", name="treasury_account_types"),
        nullable=False,
    )
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=True)
    cash_account_id = Column(Integer, ForeignKey("cash_accounts.id"), nullable=True)
    transaction_type = Column(
        SAEnum(
            "DEPOSIT",
            "WITHDRAWAL",
            "TRANSFER_IN",
            "TRANSFER_OUT",
            "FEE",
            "INTEREST",
            "CHECK_ISSUED",
            "CHECK_CLEARED",
            "CHECK_BOUNCED",
            name="treasury_tx_types",
        ),
        nullable=False,
    )
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="COP")
    description = Column(String(500))
    reference = Column(String(100))
    reference_type = Column(String(50))
    reference_id = Column(Integer, nullable=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)
    balance_after = Column(Numeric(15, 2))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company")
    bank_account = relationship("BankAccount", foreign_keys=[bank_account_id])
    cash_account = relationship("CashAccount", foreign_keys=[cash_account_id])
    journal_entry = relationship("JournalEntry")
    created_by_user = relationship("User")

    def __repr__(self):
        return f"<TreasuryTransaction(id={self.id}, type='{self.transaction_type}', amount={self.amount})>"
