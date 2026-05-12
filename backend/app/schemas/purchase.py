from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


class PaymentMethodEnum(str, Enum):
    CASH = "CASH"
    BANK_TRANSFER = "BANK_TRANSFER"
    CHECK = "CHECK"
    CREDIT_CARD = "CREDIT_CARD"
    CREDIT = "CREDIT"
    PARTIAL_CREDIT = "PARTIAL_CREDIT"


class PurchaseStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PAID = "PAID"
    PARTIAL = "PARTIAL"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"
    
class PartnerSimple(BaseModel):
    id: int
    name: str
    nit: Optional[str] = None

    class Config:
        from_attributes = True


# Purchase Item Schemas
class PurchaseItemBase(BaseModel):
    product_id: Optional[int] = None
    description: Optional[str] = "Sin descripción"
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    serial_number: Optional[str] = None
    discount_percent: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    tax_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    line_total: Decimal = Field(..., ge=0)

    @field_validator("description", mode="before")
    @classmethod
    def empty_string_to_default(cls, v):
        if v is None or v == "":
            return "Sin descripción"
        return v

    model_config = {"from_attributes": True}


class PurchaseItemCreate(PurchaseItemBase):
    pass


class PurchaseItemResponse(PurchaseItemBase):
    id: int
    purchase_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Payment Schemas
class PurchasePaymentBase(BaseModel):
    payment_method: PaymentMethodEnum
    amount: Decimal = Field(..., gt=0)
    payment_date: Optional[datetime] = None
    reference: Optional[str] = None
    notes: Optional[str] = None


class PurchasePaymentCreate(PurchasePaymentBase):
    pass


class PurchasePaymentResponse(PurchasePaymentBase):
    id: int
    purchase_id: int
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Purchase Schemas
class PurchaseBase(BaseModel):
    purchase_number: str
    partner_id: int
    purchase_date: Optional[str] = None
    due_date: Optional[str] = None
    subtotal: Decimal = Field(default=Decimal("0.00"), ge=0)
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    total_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = Field(default="COP")
    payment_method: PaymentMethodEnum = Field(default=PaymentMethodEnum.CREDIT)
    status: PurchaseStatusEnum = Field(default=PurchaseStatusEnum.DRAFT)
    notes: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def convert_empty_to_none(cls, data):
        if isinstance(data, dict):
            for field in ["purchase_date", "due_date", "notes"]:
                if field in data:
                    val = data[field]
                    if val == "" or val is None or val == "null" or val == "undefined":
                        data[field] = None
        return data

    @field_validator("purchase_date", "due_date", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "" or v is None or v == "null":
            return None
        return v

    @field_validator("purchase_number", mode="before")
    @classmethod
    def validate_purchase_number(cls, v):
        if v == "" or v is None:
            return None
        return v

    @field_validator("notes", mode="before")
    @classmethod
    def validate_notes(cls, v):
        if v == "" or v is None or v == "null":
            return None
        return v

    model_config = {"from_attributes": True}


class PurchaseCreate(PurchaseBase):
    items: List[PurchaseItemCreate] = []


class PurchaseUpdate(BaseModel):
    purchase_number: Optional[str] = None
    partner_id: Optional[int] = None
    purchase_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    payment_method: Optional[PaymentMethodEnum] = None
    status: Optional[PurchaseStatusEnum] = None
    notes: Optional[str] = None


class PurchaseResponse(BaseModel):
    id: int
    purchase_number: str
    partner_id: int
    purchase_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    subtotal: Decimal = Field(default=Decimal("0.00"), ge=0)
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    total_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = Field(default="COP")
    payment_method: PaymentMethodEnum = Field(default=PaymentMethodEnum.CREDIT)
    status: PurchaseStatusEnum = Field(default=PurchaseStatusEnum.DRAFT)
    notes: Optional[str] = None
    company_id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    items: List[PurchaseItemResponse] = []
    payments: List[PurchasePaymentResponse] = []
    partner: Optional[PartnerSimple] = None

    class Config:
        from_attributes = True


class PurchaseWithItemsCreate(BaseModel):
    purchase_number: str
    partner_id: int
    purchase_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    payment_method: PaymentMethodEnum = Field(default=PaymentMethodEnum.CREDIT)
    status: PurchaseStatusEnum = Field(default=PurchaseStatusEnum.DRAFT)
    notes: Optional[str] = None
    items: List[PurchaseItemCreate]
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = Field(default="COP")

    @model_validator(mode="before")
    @classmethod
    def convert_empty_to_none(cls, data):
        if isinstance(data, dict):
            for field in ["purchase_date", "due_date", "notes"]:
                if field in data:
                    val = data[field]
                    if val == "" or val is None or val == "null" or val == "undefined":
                        data[field] = None
        return data


# Statistics Schema
class PurchaseStatistics(BaseModel):
    total_purchases: int
    total_amount: Decimal
    paid_amount: Decimal
    pending_amount: Decimal
    overdue_count: int
    by_payment_method: dict
    by_month: list
