from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime


class CompanyBase(BaseModel):
    name: str = Field(..., max_length=255)
    nit: str = Field(..., max_length=20)
    dv: str = Field(..., max_length=1)
    legal_representative: str = Field(..., max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    regimen: str = Field(default="COMUN")
    fecha_inicio_actividades: date
    resolucion_facturacion: Optional[str] = Field(None, max_length=100)
    slogan: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    invoice_footer_note: Optional[str] = None
    repair_footer_note: Optional[str] = None

    @field_validator("nit")
    @classmethod
    def nit_must_be_valid_format(cls, v):
        if not all(c.isdigit() or c == "-" for c in v):
            raise ValueError("NIT must contain only digits and hyphens")
        return v.replace("-", "").upper()

    @field_validator("dv")
    @classmethod
    def dv_must_be_digit_or_letter(cls, v):
        if not (v.isdigit() or v.isalpha()):
            raise ValueError("DV must be a digit or letter")
        return v.upper()

    @field_validator("regimen")
    @classmethod
    def regimen_must_be_valid(cls, v):
        allowed = ["COMUN", "SIMPLE", "ESPECIAL", "NO_RESPONSABLE"]
        if v not in allowed:
            raise ValueError(f"El campo regimen '{v}' no es válido. Debe ser uno de los siguientes valores exactos: {', '.join(allowed)}")
        return v

    model_config = {"from_attributes": True, "extra": "forbid"}


class CompanyCreate(CompanyBase):
    admin_user: Optional["CompanyAdminUser"] = None


class CompanyAdminUser(BaseModel):
    email: str
    username: Optional[str] = Field(None, max_length=100)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=255)

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v):
        from app.core.security import validate_password_strength

        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v

    model_config = {"from_attributes": True}


class CompanyResponse(CompanyBase):
    id: int
    logo_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "extra": "ignore"}


CompanyCreate.model_rebuild()
