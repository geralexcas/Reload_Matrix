from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class PartnerBase(BaseModel):
    nit: Optional[str] = Field(None, max_length=20)  # Colombian Tax ID
    dv: Optional[str] = Field(None, max_length=1)  # Verification digit
    name: str = Field(..., max_length=255)
    partner_type: str = Field(default="CUSTOMER")  # SUPPLIER, CUSTOMER, BOTH
    responsibility_fiscal: Optional[str] = Field(
        None
    )  # RESPONSABLE IVA, NO RESPONSABLE, AGENTE RETENEDOR
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    credit_limit: Optional[float] = None  # Límite de crédito en COP
    is_active: bool = True

    @field_validator("nit")
    @classmethod
    def nit_must_be_valid_format(cls, v):
        if v is None:
            return v
        cleaned = v.replace(" ", "").replace(".", "").replace(",", "")
        if not all(c.isdigit() or c == "-" for c in cleaned):
            raise ValueError("NIT must contain only digits and hyphens")
        return cleaned.replace("-", "").upper()

    @field_validator("dv")
    @classmethod
    def dv_must_be_digit_or_letter(cls, v):
        if v is None:
            return v
        if not (v.isdigit() or v.isalpha()):
            raise ValueError("DV must be a digit or letter")
        return v.upper()

    @field_validator("partner_type")
    @classmethod
    def partner_type_must_be_valid(cls, v):
        allowed = ["SUPPLIER", "CUSTOMER", "BOTH"]
        if v not in allowed:
            raise ValueError(f"Partner type must be one of {allowed}")
        return v

    @field_validator("responsibility_fiscal")
    @classmethod
    def responsibility_fiscal_must_be_valid(cls, v):
        if v is None:
            return v
        allowed = ["RESPONSABLE IVA", "NO RESPONSABLE", "AGENTE RETENEDOR"]
        if v not in allowed:
            raise ValueError(f"El campo responsibility_fiscal '{v}' no es válido. Debe ser uno de los siguientes valores exactos: {', '.join(allowed)}")
        return v

    model_config = {"from_attributes": True}


class PartnerCreate(PartnerBase):
    pass


class PartnerResponse(PartnerBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
