from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# Invoice Schema
class InvoiceBase(BaseModel):
    invoice_number: Optional[str] = Field(None, max_length=50)
    invoice_type: str  # SALE or PURCHASE
    partner_id: int
    issue_date: datetime
    due_date: Optional[datetime] = None
    total_amount: Decimal
    currency: str = Field(default="COP", max_length=3)
    status: str = Field(default="DRAFT")  # DRAFT, ISSUED, PAID, CANCELLED
    # Para facturación electrónica en Colombia
    cufe: Optional[str] = Field(None, max_length=100)
    xml_ubl: Optional[str] = None
    estado_dian: Optional[str] = Field(None)  # BORRADOR, ENVIADO, ACEPTADO, RECHAZADO
    motivo_rechazo: Optional[str] = Field(
        None
    )  # Motivo de rechazo por la DIAN, si aplica

    @field_validator("invoice_type")
    @classmethod
    def invoice_type_must_be_valid(cls, v):
        allowed = ["SALE", "PURCHASE", "CUENTA_COBRO"]
        if v not in allowed:
            raise ValueError(f"Invoice type must be one of {allowed}")
        return v

    @field_validator("currency")
    @classmethod
    def currency_must_be_valid(cls, v):
        # Basic validation for currency code (ISO 4217)
        if len(v) != 3 or not v.isalpha():
            raise ValueError("Currency must be a 3-letter code (ISO 4217)")
        return v.upper()

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v):
        allowed = ["DRAFT", "ISSUED", "PAID", "CANCELLED"]
        if v not in allowed:
            raise ValueError(f"Invoice status must be one of {allowed}")
        return v

    model_config = {"from_attributes": True}


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceResponse(InvoiceBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    # Partner denormalized fields (populated from relationship)
    partner_name: Optional[str] = None
    partner_nit: Optional[str] = None
    partner_address: Optional[str] = None
    partner_phone: Optional[str] = None
    # Calculated totals
    subtotal: Optional[Decimal] = None
    vat_amount: Optional[Decimal] = None

    model_config = {"from_attributes": True}


# Invoice Item Schema
class InvoiceItemBase(BaseModel):
    description: str = Field(..., max_length=255)
    quantity: Decimal = Field(..., decimal_places=2)
    unit_price: Decimal = Field(..., decimal_places=2)
    discount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    tax_rate: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    tax_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    line_total: Decimal
    # Para referencia a productos en inventario (opcional)
    product_id: Optional[int] = None
    # Agrupador para componentes de un equipo ensamblado (PC Armado)
    assembly_group_id: Optional[str] = Field(None, max_length=50)

    @field_validator(
        "quantity", "unit_price", "discount", "tax_rate", "tax_amount", "line_total"
    )
    @classmethod
    def amounts_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("Amounts must be non-negative")
        return v

    model_config = {"from_attributes": True}


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemResponse(InvoiceItemBase):
    id: int
    invoice_id: int

    model_config = {"from_attributes": True}


# Invoice with Items (for creating an invoice with items in one go)
class InvoiceWithItemsCreate(BaseModel):
    invoice_number: Optional[str] = Field(None, max_length=50)
    invoice_type: str  # SALE or PURCHASE
    partner_id: int
    issue_date: datetime
    due_date: Optional[datetime] = None
    currency: str = Field(default="COP", max_length=3)
    status: str = Field(default="DRAFT")
    cufe: Optional[str] = Field(None, max_length=100)
    xml_ubl: Optional[str] = None
    estado_dian: Optional[str] = Field(None)  # BORRADOR, ENVIADO, ACEPTADO, RECHAZADO
    motivo_rechazo: Optional[str] = Field(
        None
    )  # Motivo de rechazo por la DIAN, si aplica
    total_amount: Decimal
    is_paid: bool = False
    payment_method: Optional[str] = None
    payment_account_type: Optional[str] = None
    payment_account_id: Optional[int] = None
    wallet_amount_applied: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    repair_id: Optional[int] = None
    items: List[InvoiceItemCreate]

    @field_validator("invoice_type")
    @classmethod
    def invoice_type_must_be_valid(cls, v):
        allowed = ["SALE", "PURCHASE", "CUENTA_COBRO"]
        if v not in allowed:
            raise ValueError(f"Invoice type must be one of {allowed}")
        return v

    @field_validator("currency")
    @classmethod
    def currency_must_be_valid(cls, v):
        if len(v) != 3 or not v.isalpha():
            raise ValueError("Currency must be a 3-letter code (ISO 4217)")
        return v.upper()

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v):
        allowed = ["DRAFT", "ISSUED", "PAID", "CANCELLED"]
        if v not in allowed:
            raise ValueError(f"Invoice status must be one of {allowed}")
        return v

    @field_validator("items")
    @classmethod
    def must_have_at_least_one_item(cls, v):
        if len(v) < 1:
            raise ValueError("Invoice must have at least one item")
        return v

    model_config = {"from_attributes": True}


# For responses, we might want to include the items
class InvoiceWithItemsResponse(InvoiceResponse):
    items: List[InvoiceItemResponse] = []

    model_config = {"from_attributes": True}


# Credit / Debit Note Schemas
class CreditDebitNoteBase(BaseModel):
    note_type: str  # CREDIT or DEBIT
    reason: str = Field(..., max_length=500)
    amount: Decimal = Field(..., decimal_places=2)

    @field_validator("note_type")
    @classmethod
    def note_type_must_be_valid(cls, v):
        allowed = ["CREDIT", "DEBIT"]
        if v not in allowed:
            raise ValueError(f"Note type must be one of {allowed}")
        return v

    model_config = {"from_attributes": True}


class CreditDebitNoteCreate(CreditDebitNoteBase):
    original_invoice_id: int


class CreditDebitNoteResponse(CreditDebitNoteBase):
    id: int
    company_id: int
    original_invoice_id: int
    note_number: str
    cufe: Optional[str] = None
    xml_ubl: Optional[str] = None
    estado_dian: Optional[str] = None
    motivo_rechazo: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
