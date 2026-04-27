from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    role: str = Field(default="VENDEDOR")

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v):
        allowed = [
            "ADMINISTRADOR",
            "CONTADOR",
            "TECNICO",
            "VENDEDOR",
            "BODEGUERO",
            "FACTURADOR",
        ]
        if v not in allowed:
            raise ValueError(f"Role must be one of {allowed}")
        return v

    model_config = {"from_attributes": True}


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v):
        from app.core.security import validate_password_strength

        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    company_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserMeResponse(UserResponse):
    permissions: List[str] = []
    last_login: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def populate_additional_fields(cls, data):
        if hasattr(data, "permissions"):
            data.permissions = [p.name for p in data.permissions]
        
        # map last_login from updated_at if available
        if hasattr(data, "updated_at"):
            data.last_login = data.updated_at
            
        return data

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str

    model_config = {"from_attributes": True}


class TokenData(BaseModel):
    username: Optional[str] = None

    model_config = {"from_attributes": True}


class RefreshToken(BaseModel):
    refresh_token: str

    model_config = {"from_attributes": True}
