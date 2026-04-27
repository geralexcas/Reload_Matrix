from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Enum,
    Boolean,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    balance = Column(Numeric(15, 2), default=0.00)
    loyalty_points = Column(Numeric(15, 2), default=0.00)
    currency = Column(String(3), default="COP")
    is_active = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company")
    partner = relationship("Partner")
    user = relationship("User")
    transactions = relationship(
        "WalletTransaction", back_populates="wallet", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Wallet(id={self.id}, balance={self.balance}, currency={self.currency})>"
        )


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"))
    transaction_type = Column(
        Enum(
            "DEPOSIT",
            "WITHDRAWAL",
            "TRANSFER_IN",
            "TRANSFER_OUT",
            "LOYALTY_EARN",
            "LOYALTY_REDEEM",
            name="wallet_tx_types",
        ),
        nullable=False,
    )
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(String(500))
    reference_type = Column(String(50))
    reference_id = Column(Integer, nullable=True)
    balance_after = Column(Numeric(15, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    wallet = relationship("Wallet", back_populates="transactions")

    def __repr__(self):
        return f"<WalletTransaction(id={self.id}, type='{self.transaction_type}', amount={self.amount})>"
