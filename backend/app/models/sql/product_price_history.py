from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, func
from app.core.database import Base

class ProductPriceHistory(Base):
    __tablename__ = "product_price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    price = Column(Numeric(15, 2), nullable=False)
    effective_date = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ProductPriceHistory(product_id={self.product_id}, price={self.price})>"
