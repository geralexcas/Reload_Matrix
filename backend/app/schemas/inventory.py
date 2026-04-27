from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    sku: str = Field(..., max_length=50)
    barcode: Optional[str] = Field(
        None, max_length=100
    )  # Código de barras (EAN, UPC, etc.)
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)  # Marca del producto
    model: Optional[str] = Field(None, max_length=100)  # Modelo del producto
    unit_of_measure: str = Field(
        default="UNIDAD", max_length=50
    )  # UNIDAD, KG, LITRO, etc.
    purchase_price: Decimal = Field(..., decimal_places=2)
    sale_price: Decimal = Field(..., decimal_places=2)
    stock_level: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    min_stock_level: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    max_stock_level: Decimal = Field(default=Decimal("999999.99"), decimal_places=2)
    supplier_id: Optional[int] = None
    is_active: bool = True

    @field_validator("barcode")
    @classmethod
    def barcode_must_be_alphanumeric_or_empty(cls, v):
        if v is not None and len(v) > 0:
            if not v.replace("-", "").replace(" ", "").isalnum():
                raise ValueError(
                    "Barcode must be alphanumeric (letters, numbers, dashes)"
                )
        return v

    @field_validator(
        "purchase_price",
        "sale_price",
        "stock_level",
        "min_stock_level",
        "max_stock_level",
    )
    @classmethod
    def amounts_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("Amounts must be non-negative")
        return v

    model_config = {"from_attributes": True}


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
