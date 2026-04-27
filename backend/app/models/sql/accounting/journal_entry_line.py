from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class JournalEntryLine(Base):
    __tablename__ = "journal_entry_lines"

    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"))
    account_id = Column(Integer, ForeignKey("chart_of_accounts.id"))
    debit_amount = Column(Numeric(15, 2), default=0.00)
    credit_amount = Column(Numeric(15, 2), default=0.00)
    description = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("ChartOfAccounts")

    def __repr__(self):
        return f"<JournalEntryLine(id={self.id}, journal_entry_id={self.journal_entry_id}, account_id={self.account_id}, debit={self.debit_amount}, credit={self.credit_amount})>"
