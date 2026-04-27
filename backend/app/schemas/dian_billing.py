from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class DianBillingRangeBase(BaseModel):
    resolution: str = Field(..., max_length=100)
    prefix: str = Field(..., max_length=10)
    from_number: int
    to_number: int
    approval_date: date
    expiration_date: date

    model_config = {"from_attributes": True}


class DianBillingRangeCreate(DianBillingRangeBase):
    pass


class DianBillingRangeResponse(DianBillingRangeBase):
    id: int
    company_id: int
    next_number: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
