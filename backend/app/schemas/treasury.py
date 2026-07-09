from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# Bank Account Schemas
class BankAccountBase(BaseModel):
    name: str = Field(..., max_length=255)
    bank_name: str = Field(..., max_length=255)
    account_number: str = Field(..., max_length=50)
    account_type: str = "CHECKING"
    currency: str = "COP"
    initial_balance: Decimal = Decimal("0.00")
    branch_office: Optional[str] = Field(None, max_length=255)
    swift_code: Optional[str] = Field(None, max_length=20)
    routing_number: Optional[str] = Field(None, max_length=20)
    linked_account_id: Optional[int] = None

    @field_validator("account_type")
    @classmethod
    def account_type_must_be_valid(cls, v):
        allowed = ["CHECKING", "SAVINGS", "TIME_DEPOSIT"]
        if v not in allowed:
            raise ValueError(f"Account type must be one of {allowed}")
        return v

    model_config = {"from_attributes": True}


class BankAccountCreate(BankAccountBase):
    pass


class BankAccountUpdate(BaseModel):
    name: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    account_type: Optional[str] = None
    currency: Optional[str] = None
    branch_office: Optional[str] = None
    swift_code: Optional[str] = None
    routing_number: Optional[str] = None
    linked_account_id: Optional[int] = None
    is_active: Optional[bool] = None

    model_config = {"from_attributes": True}


class BankAccountResponse(BankAccountBase):
    id: int
    company_id: int
    current_balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Cash Account Schemas
class CashAccountBase(BaseModel):
    name: str = Field(..., max_length=255)
    account_type: str = "MAIN_CASH"
    currency: str = "COP"
    initial_balance: Decimal = Decimal("0.00")
    responsible_user_id: Optional[int] = None
    max_petty_cash_amount: Optional[Decimal] = None
    linked_account_id: Optional[int] = None

    @field_validator("account_type")
    @classmethod
    def account_type_must_be_valid(cls, v):
        allowed = ["MAIN_CASH", "PETTY_CASH", "REGISTER_CASH"]
        if v not in allowed:
            raise ValueError(f"Account type must be one of {allowed}")
        return v

    model_config = {"from_attributes": True}


class CashAccountCreate(CashAccountBase):
    pass


class CashAccountUpdate(BaseModel):
    name: Optional[str] = None
    account_type: Optional[str] = None
    currency: Optional[str] = None
    responsible_user_id: Optional[int] = None
    max_petty_cash_amount: Optional[Decimal] = None
    linked_account_id: Optional[int] = None
    is_active: Optional[bool] = None

    model_config = {"from_attributes": True}


class CashAccountResponse(CashAccountBase):
    id: int
    company_id: int
    current_balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Treasury Transaction Schemas
class TreasuryTransactionResponse(BaseModel):
    id: int
    company_id: int
    account_type: str
    bank_account_id: Optional[int] = None
    cash_account_id: Optional[int] = None
    transaction_type: str
    amount: Decimal
    currency: str
    description: Optional[str] = None
    reference: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    journal_entry_id: Optional[int] = None
    balance_after: Optional[Decimal] = None
    created_by: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# Operation Request Schemas
class DepositRequest(BaseModel):
    account_type: str = Field(..., description="BANK or CASH")
    account_id: int
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    reference: Optional[str] = None

    @field_validator("account_type")
    @classmethod
    def account_type_must_be_valid(cls, v):
        allowed = ["BANK", "CASH"]
        if v not in allowed:
            raise ValueError(f"Account type must be one of {allowed}")
        return v

    model_config = {"from_attributes": True}


class WithdrawalRequest(BaseModel):
    account_type: str = Field(..., description="BANK or CASH")
    account_id: int
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    reference: Optional[str] = None

    @field_validator("account_type")
    @classmethod
    def account_type_must_be_valid(cls, v):
        allowed = ["BANK", "CASH"]
        if v not in allowed:
            raise ValueError(f"Account type must be one of {allowed}")
        return v

    model_config = {"from_attributes": True}


class TransferRequest(BaseModel):
    from_account_type: str = Field(..., description="BANK or CASH")
    from_account_id: int
    to_account_type: str = Field(..., description="BANK or CASH")
    to_account_id: int
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    reference: Optional[str] = None

    @field_validator("from_account_type", "to_account_type")
    @classmethod
    def account_types_must_be_valid(cls, v):
        allowed = ["BANK", "CASH"]
        if v not in allowed:
            raise ValueError(f"Account type must be one of {allowed}")
        return v

    model_config = {"from_attributes": True}


# Check Register Schemas
class CheckRegisterBase(BaseModel):
    bank_account_id: int
    check_number: str = Field(..., max_length=30)
    payee: str = Field(..., max_length=255)
    amount: Decimal = Field(..., gt=0)
    issue_date: datetime
    notes: Optional[str] = Field(None, max_length=500)

    model_config = {"from_attributes": True}


class CheckRegisterCreate(CheckRegisterBase):
    pass


class CheckRegisterResponse(CheckRegisterBase):
    id: int
    company_id: int
    status: str
    cleared_date: Optional[datetime] = None
    linked_transaction_id: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CheckStatusUpdate(BaseModel):
    status: str
    bounce_fee: Optional[Decimal] = None

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v):
        allowed = ["ISSUED", "DELIVERED", "CLEARED", "BOUNCED", "VOIDED"]
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v

    model_config = {"from_attributes": True}


# Summary and Report Schemas
class TreasurySummaryAccount(BaseModel):
    id: int
    name: str
    type: str
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    account_type_detail: Optional[str] = None
    balance: Decimal
    currency: str

    model_config = {"from_attributes": True}


class TreasurySummaryResponse(BaseModel):
    company_id: int
    total_banks: Decimal
    total_cash: Decimal
    total_treasury: Decimal
    bank_accounts: List[TreasurySummaryAccount] = []
    cash_accounts: List[TreasurySummaryAccount] = []

    model_config = {"from_attributes": True}


class CashFlowEntry(BaseModel):
    date: datetime
    account_type: str
    account_name: str
    transaction_type: str
    amount: Decimal
    description: Optional[str] = None
    reference: Optional[str] = None

    model_config = {"from_attributes": True}


class CashFlowResponse(BaseModel):
    company_id: int
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    total_inflows: Decimal
    total_outflows: Decimal
    net_flow: Decimal
    entries: List[CashFlowEntry] = []

    model_config = {"from_attributes": True}


# Bank Reconciliation Schemas
class BankReconciliationCreate(BaseModel):
    bank_account_id: int
    statement_date: datetime
    statement_balance: Decimal
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class ReconciliationLineResponse(BaseModel):
    id: int
    reconciliation_id: int
    treasury_transaction_id: Optional[int] = None
    is_matched: bool
    amount: Decimal
    description: Optional[str] = None
    statement_date: Optional[datetime] = None
    system_date: Optional[datetime] = None
    difference: Decimal
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class BankReconciliationResponse(BaseModel):
    id: int
    company_id: int
    bank_account_id: int
    statement_date: datetime
    statement_balance: Decimal
    system_balance: Decimal
    outstanding_deposits: Decimal
    outstanding_checks: Decimal
    bank_fees_not_recorded: Decimal
    interest_not_recorded: Decimal
    adjusted_balance: Optional[Decimal] = None
    is_balanced: bool
    status: str
    reconciled_by: Optional[int] = None
    reconciled_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    lines: List[ReconciliationLineResponse] = []

    model_config = {"from_attributes": True}


class MatchTransactionRequest(BaseModel):
    treasury_transaction_id: int
    statement_date: datetime
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class AddOutstandingItemRequest(BaseModel):
    amount: Decimal
    description: str
    item_type: str = Field(..., description="OUTSTANDING_DEPOSIT or OUTSTANDING_CHECK")

    model_config = {"from_attributes": True}
