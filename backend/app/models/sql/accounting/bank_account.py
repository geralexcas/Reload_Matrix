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


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    bank_name = Column(String(255), nullable=False)
    account_number = Column(String(50), nullable=False)
    account_type = Column(
        SAEnum("CHECKING", "SAVINGS", "TIME_DEPOSIT", name="bank_account_types"),
        nullable=False,
        default="CHECKING",
    )
    currency = Column(String(3), default="COP")
    initial_balance = Column(Numeric(15, 2), default=0.00)
    current_balance = Column(Numeric(15, 2), default=0.00)
    is_active = Column(Boolean, default=True)
    branch_office = Column(String(255))
    swift_code = Column(String(20))
    routing_number = Column(String(20))
    linked_account_id = Column(
        Integer, ForeignKey("chart_of_accounts.id"), nullable=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company")
    linked_account = relationship("ChartOfAccounts")
    transactions = relationship(
        "TreasuryTransaction",
        back_populates="bank_account",
        foreign_keys="TreasuryTransaction.bank_account_id",
    )
    checks = relationship("CheckRegister", back_populates="bank_account")

    def __repr__(self):
        return f"<BankAccount(id={self.id}, bank='{self.bank_name}', account='{self.account_number}')>"
