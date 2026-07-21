from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class RevokedToken(Base):
    """Denylist de jtis de access tokens revocados (logout).

    ponytail: purge lazy — access token vive 30 min, la tabla se mantiene
    pequenia.  Si crece, agregar job que borre `expires_at < now()` en scheduler.
    """

    __tablename__ = "revoked_tokens"

    jti = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<RevokedToken(jti='{self.jti}', user_id={self.user_id})>"