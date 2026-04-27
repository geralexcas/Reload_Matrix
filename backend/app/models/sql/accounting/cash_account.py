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


class CashAccount(Base):
    __tablename__ = "cash_accounts"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    account_type = Column(
        SAEnum("MAIN_CASH", "PETTY_CASH", "REGISTER_CASH", name="cash_account_types"),
        nullable=False,
        default="MAIN_CASH",
    )
    currency = Column(String(3), default="COP")
    initial_balance = Column(Numeric(15, 2), default=0.00)
    current_balance = Column(Numeric(15, 2), default=0.00)
    responsible_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    max_petty_cash_amount = Column(Numeric(15, 2), nullable=True)
    is_active = Column(Boolean, default=True)
    linked_account_id = Column(
        Integer, ForeignKey("chart_of_accounts.id"), nullable=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company")
    responsible_user = relationship("User")
    linked_account = relationship("ChartOfAccounts")
    transactions = relationship(
        "TreasuryTransaction",
        back_populates="cash_account",
        foreign_keys="TreasuryTransaction.cash_account_id",
    )

    def __repr__(self):
        return f"<CashAccount(id={self.id}, name='{self.name}', type='{self.account_type}')>"
