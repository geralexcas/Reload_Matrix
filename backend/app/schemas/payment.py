from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class POSPayment(BaseModel):
    is_paid: bool = False
    payment_method: str = Field(default="CASH")
    amount_paid: Decimal = Field(default=Decimal("0.00"))
    payment_account_type: Optional[str] = None
    payment_account_id: Optional[int] = None
    reference: Optional[str] = None
