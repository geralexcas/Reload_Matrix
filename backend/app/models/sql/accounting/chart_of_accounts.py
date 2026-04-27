from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ChartOfAccounts(Base):
    __tablename__ = "chart_of_accounts"
    __table_args__ = (
        UniqueConstraint("code", "company_id", name="uq_chart_code_company"),
    )

    id = Column(Integer, primary_key=True, index=True)
    code = Column(
        String(20), nullable=False, index=True
    )  # Account code (unique per company)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    account_type = Column(
        Enum(
            "ASSET", "LIABILITY", "EQUITY", "REVENUE", "EXPENSE", name="account_types"
        ),
        nullable=False,
    )
    is_active = Column(Boolean, default=True)
    parent_id = Column(
        Integer, ForeignKey("chart_of_accounts.id")
    )  # For hierarchical accounts (optional)
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    company = relationship("Company")
    parent = relationship(
        "ChartOfAccounts", remote_side=[id]
    )  # Self-referential for hierarchy
    children = relationship("ChartOfAccounts")  # For reverse relationship

    def __repr__(self):
        return f"<ChartOfAccounts(id={self.id}, code='{self.code}', name='{self.name}', type='{self.account_type}')>"
