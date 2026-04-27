from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.schemas.partners import PartnerResponse
from app.schemas.user import UserResponse


# Warranty Schema
class WarrantyBase(BaseModel):
    repair_order_id: int
    repair_item_id: Optional[int] = None
    warranty_type: str = Field(default="SERVICE")
    start_date: datetime
    end_date: datetime
    description: Optional[str] = Field(None, max_length=1000)
    terms_and_conditions: Optional[str] = None

    @field_validator("warranty_type")
    @classmethod
    def warranty_type_must_be_valid(cls, v):
        allowed = ["MANUFACTURER", "SERVICE", "PARTS"]
        if v not in allowed:
            raise ValueError(f"Warranty type must be one of {allowed}")
        return v

    model_config = {"from_attributes": True}


class WarrantyCreate(WarrantyBase):
    pass


class WarrantyClaim(BaseModel):
    claim_description: str = Field(..., max_length=1000)
    claim_resolution: Optional[str] = Field(None, max_length=1000)

    @field_validator("claim_description")
    @classmethod
    def claim_description_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Claim description must not be empty")
        return v.strip()

    model_config = {"from_attributes": True}


class WarrantyResponse(WarrantyBase):
    id: int
    company_id: int
    status: str
    claim_date: Optional[datetime] = None
    claim_description: Optional[str] = None
    claim_resolution: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Technician Schema
class TechnicianBase(BaseModel):
    employee_id: str = Field(..., max_length=50)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    specialty: Optional[str] = Field(None, max_length=200)
    is_active: bool = True

    @field_validator("employee_id")
    @classmethod
    def employee_id_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Employee ID must not be empty")
        return v.strip()

    model_config = {"from_attributes": True}


class TechnicianCreate(TechnicianBase):
    pass


class TechnicianResponse(TechnicianBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Repair Order Schema
class RepairOrderBase(BaseModel):
    order_number: Optional[str] = Field(None, max_length=50)
    partner_id: int
    issue_date: datetime
    expected_completion_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    description: str = Field(..., max_length=500)
    status: str = Field(
        default="RECEIVED"
    )  # RECEIVED, IN_REPAIR, WAITING_PARTS, COMPLETED, DELIVERED, CANCELLED
    total_amount: Decimal = Field(default=Decimal("0.00"))
    # Para facturación electrónica en Colombia
    cufe: Optional[str] = Field(None, max_length=100)
    xml_ubl: Optional[str] = None
    dian_response: Optional[str] = None
    technician_id: Optional[int] = None  # ID del técnico asignado

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v):
        allowed = [
            "RECEIVED",
            "IN_REPAIR",
            "WAITING_PARTS",
            "COMPLETED",
            "DELIVERED",
            "CANCELLED",
        ]
        if v not in allowed:
            raise ValueError(f"Repair order status must be one of {allowed}")
        return v

    model_config = {"from_attributes": True}


class RepairOrderCreate(RepairOrderBase):
    pass





# Repair Item Schema
class RepairItemBase(BaseModel):
    description: str = Field(..., max_length=255)
    serial_number: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    issue_reported: Optional[str] = Field(None, max_length=500)
    quantity: int = Field(default=1)
    unit_cost: Decimal = Field(default=Decimal("0.00"))
    discount: Decimal = Field(default=Decimal("0.00"))
    tax_rate: Decimal = Field(default=Decimal("0.00"))
    tax_amount: Decimal = Field(default=Decimal("0.00"))
    line_total: Decimal = Field(default=Decimal("0.00"))
    # Para referencia a productos en inventario (opcional)
    product_id: Optional[int] = None
    warranty_status: str = Field(
        default="NO_WARRANTY"
    )  # NO_WARRANTY, IN_WARRANTY, WARRANTY_VOID
    warranty_days: Optional[int] = Field(None, description="Días de garantía")

    @field_validator(
        "quantity", "unit_cost", "discount", "tax_rate", "tax_amount", "line_total"
    )
    @classmethod
    def amounts_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("Amounts must be non-negative")
        return v

    @field_validator("warranty_status")
    @classmethod
    def warranty_status_must_be_valid(cls, v):
        allowed = ["NO_WARRANTY", "IN_WARRANTY", "WARRANTY_VOID"]
        if v not in allowed:
            raise ValueError(f"Warranty status must be one of {allowed}")
        return v

    model_config = {"from_attributes": True}


class RepairItemCreate(RepairItemBase):
    pass


class RepairItemResponse(BaseModel):
    id: int
    repair_order_id: int
    description: Optional[str] = None
    serial_number: Optional[str] = None
    model: Optional[str] = None
    brand: Optional[str] = None
    issue_reported: Optional[str] = None
    quantity: int = 1
    unit_cost: Decimal = Decimal("0.00")
    discount: Decimal = Decimal("0.00")
    tax_rate: Decimal = Decimal("0.00")
    tax_amount: Decimal = Decimal("0.00")
    line_total: Decimal = Decimal("0.00")
    product_id: Optional[int] = None
    warranty_status: str = "NO_WARRANTY"
    warranty_days: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Repair Order with Items (for creating a repair order with items in one go)
class RepairOrderWithItemsCreate(BaseModel):
    order_number: Optional[str] = Field(None, max_length=50)
    partner_id: int
    technician_id: Optional[int] = None  # ID del técnico asignado
    issue_date: datetime
    expected_delivery_date: Optional[datetime] = None  # Fecha esperada de entrega
    actual_delivery_date: Optional[datetime] = None  # Fecha real de entrega
    problem_description: str = Field(
        ..., max_length=1000
    )  # Descripción del problema reportado
    diagnosis: Optional[str] = Field(None, max_length=1000)  # Diagnóstico técnico
    service_notes: Optional[str] = Field(None, max_length=2000)  # Notas de servicio
    status: str = Field(
        default="RECEIVED"
    )  # RECEIVED, DIAGNOSIS, APPROVED, IN_REPAIR, WAITING_PARTS, READY, DELIVERED, CANCELLED
    warranty_applied: bool = Field(default=False)  # Si se aplica garantía
    total_labor_cost: Decimal = Field(
        default=Decimal("0.00")
    )  # Costo de mano de obra
    total_parts_cost: Decimal = Field(
        default=Decimal("0.00")
    )  # Costo de repuestos
    total_amount: Decimal = Field(
        default=Decimal("0.00")
    )  # Total a facturar
    # Para facturación electrónica en Colombia
    cufe: Optional[str] = Field(None, max_length=100)
    xml_ubl: Optional[str] = None
    estado_dian: Optional[str] = Field(None)  # BORRADOR, ENVIADO, ACEPTADO, RECHAZADO
    motivo_rechazo: Optional[str] = Field(
        None
    )  # Motivo de rechazo por la DIAN, si aplica
    items: List[RepairItemCreate]

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v):
        allowed = [
            "RECEIVED",
            "DIAGNOSIS",
            "APPROVED",
            "IN_REPAIR",
            "WAITING_PARTS",
            "READY",
            "DELIVERED",
            "CANCELLED",
        ]
        if v not in allowed:
            raise ValueError(f"Repair order status must be one of {allowed}")
        return v

    @field_validator("items")
    @classmethod
    def must_have_at_least_one_item(cls, v):
        if len(v) < 1:
            raise ValueError("Repair order must have at least one item")
        return v

    model_config = {"from_attributes": True}


class RepairOrderResponse(BaseModel):
    id: int
    order_number: str
    partner_id: int
    partner: Optional[PartnerResponse] = None
    technician_id: Optional[int] = None
    technician: Optional[UserResponse] = None
    issue_date: datetime
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    problem_description: Optional[str] = None
    description: Optional[str] = None  # Override from RepairOrderBase
    diagnosis: Optional[str] = None
    service_notes: Optional[str] = None
    status: str = "RECEIVED"
    warranty_applied: bool = False
    total_labor_cost: Decimal = Decimal("0.00")
    total_parts_cost: Decimal = Decimal("0.00")
    total_amount: Decimal = Decimal("0.00")
    currency: str = "COP"
    cufe: Optional[str] = None
    xml_ubl: Optional[str] = None
    estado_dian: Optional[str] = None
    motivo_rechazo: Optional[str] = None
    invoice_id: Optional[int] = None
    company_id: int
    items: List[RepairItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# For responses, we might want to include the items
class RepairOrderWithItemsResponse(RepairOrderResponse):
    items: List[RepairItemResponse] = []

    model_config = {"from_attributes": True}


# Simplified schema for form submission (without items)
class RepairOrderSimpleCreate(BaseModel):
    order_number: Optional[str] = Field(None, max_length=50)
    partner_id: int
    technician_id: Optional[int] = None
    issue_date: datetime
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    problem_description: str = Field(..., max_length=1000)
    diagnosis: Optional[str] = Field(None, max_length=1000)
    service_notes: Optional[str] = Field(None, max_length=2000)
    status: str = Field(default="RECEIVED")
    warranty_applied: bool = Field(default=False)
    total_labor_cost: Decimal = Field(default=Decimal("0.00"))
    total_parts_cost: Decimal = Field(default=Decimal("0.00"))
    total_amount: Decimal = Field(default=Decimal("0.00"))
    # Primary item details
    device_type: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v):
        allowed = [
            "RECEIVED",
            "DIAGNOSIS",
            "APPROVED",
            "IN_REPAIR",
            "WAITING_PARTS",
            "READY",
            "DELIVERED",
            "CANCELLED",
        ]
        if v not in allowed:
            raise ValueError(f"Repair order status must be one of {allowed}")
        return v

    model_config = {"from_attributes": True}


# Schema for updating repair orders
class RepairOrderUpdate(BaseModel):
    order_number: Optional[str] = Field(None, max_length=50)
    partner_id: Optional[int] = None
    technician_id: Optional[int] = None
    issue_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    problem_description: Optional[str] = Field(None, max_length=1000)
    diagnosis: Optional[str] = Field(None, max_length=1000)
    service_notes: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = None
    warranty_applied: Optional[bool] = None
    total_labor_cost: Optional[Decimal] = Field(None)
    total_parts_cost: Optional[Decimal] = Field(None)
    total_amount: Optional[Decimal] = Field(None)

    @field_validator("expected_delivery_date", "actual_delivery_date", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v

    model_config = {"from_attributes": True}
