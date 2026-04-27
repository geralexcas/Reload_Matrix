from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    Text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    module = Column(String(50), nullable=False)  # accounting, invoicing, partners, etc.
    action = Column(String(50), nullable=False)  # create, read, update, delete, approve

    model_config = {"from_attributes": True}


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    action = Column(
        Enum("CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT", name="audit_actions"),
        nullable=False,
    )
    entity_type = Column(String(50), nullable=False)  # Invoice, Partner, JournalEntry
    entity_id = Column(Integer, nullable=True)
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    company = relationship("Company")

    model_config = {"from_attributes": True}
