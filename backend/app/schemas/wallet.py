from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class WalletBase(BaseModel):
    partner_id: Optional[int] = None
    user_id: Optional[int] = None
    balance: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    currency: str = Field(default="COP", max_length=3)
    is_active: bool = True

    @field_validator("balance")
    @classmethod
    def balance_non_negative(cls, v):
        if v < 0:
            raise ValueError("Balance cannot be negative")
        return v

    model_config = {"from_attributes": True}


class WalletCreate(WalletBase):
    pass


class WalletResponse(WalletBase):
    id: int
    company_id: int
    loyalty_points: Optional[Decimal] = Decimal("0.00")
    partner_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def populate_partner_name(cls, data):
        if hasattr(data, "partner") and data.partner:
            data.partner_name = data.partner.name
        elif isinstance(data, dict) and "partner" in data and data["partner"]:
            data["partner_name"] = data["partner"]["name"]
        return data

    model_config = {"from_attributes": True}


class WalletTransactionBase(BaseModel):
    transaction_type: str
    amount: Decimal = Field(..., decimal_places=2)
    description: Optional[str] = Field(None, max_length=500)
    reference_type: Optional[str] = Field(None, max_length=50)
    reference_id: Optional[int] = None

    @field_validator("transaction_type")
    @classmethod
    def tx_type_must_be_valid(cls, v):
        allowed = ["DEPOSIT", "WITHDRAWAL", "TRANSFER_IN", "TRANSFER_OUT"]
        if v not in allowed:
            raise ValueError(f"Transaction type must be one of {allowed}")
        return v

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    model_config = {"from_attributes": True}


class WalletTransactionCreate(WalletTransactionBase):
    pass


class WalletTransactionResponse(WalletTransactionBase):
    id: int
    wallet_id: int
    balance_after: Optional[Decimal] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WalletWithTransactionsResponse(WalletResponse):
    transactions: List[WalletTransactionResponse] = []

    model_config = {"from_attributes": True}
