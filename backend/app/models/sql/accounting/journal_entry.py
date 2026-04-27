from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    entry_date = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    description = Column(String(500))
    reference = Column(String(100))  # e.g., invoice number, payment reference
    is_posted = Column(
        Boolean, default=False
    )  # Whether the entry has been posted to the ledger
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    company = relationship("Company")
    lines = relationship(
        "JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<JournalEntry(id={self.id}, date='{self.entry_date}', description='{self.description}')>"
